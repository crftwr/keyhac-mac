//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-11.
//

import Foundation
import CoreGraphics
import Carbon

public class Hook {
    
    private static let instance = Hook()
    public static func getInstance() -> Hook { return instance }
    
    enum VK: Int64 {
        case CAPITAL = 0x39
    }
    
    static let modifierFlags = CGEventFlags(rawValue: UInt64(
        NX_DEVICELCTLKEYMASK | NX_DEVICERCTLKEYMASK | NX_COMMANDMASK |
        NX_DEVICELSHIFTKEYMASK | NX_DEVICERSHIFTKEYMASK | NX_SHIFTMASK |
        NX_DEVICELALTKEYMASK | NX_DEVICERALTKEYMASK | NX_ALTERNATEMASK |
        NX_DEVICELCMDKEYMASK | NX_DEVICERCMDKEYMASK | NX_COMMANDMASK |
        NX_SECONDARYFNMASK
    ))
    
    enum KeyEventDirection {
        case keyDown
        case keyUp
    }
    
    enum KeyEventSource {
        case real
        case translated
        case replay
    }
    
    // Allow send virtual keys from threads
    private let lock = NSRecursiveLock()
    
    // Keyboard hook at OS level
    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var eventSourceForTranslated: CGEventSource?
    var eventSourceForReplay: CGEventSource?

    var timer: Timer?
    static let timerInterval = 0.0333
    
    // Sanity check
    static let sanityCheckInterval = 1.0
    var sanityCheckCountDown = sanityCheckInterval
    
    // Event order handling
    var numPendingVirtualKeyEvents: Int = 0
    var deferredRealKeyEvents: [CGEvent] = []
    static let flushRealKeyEventsTimeout = 0.2
    var flushRealKeyEventsCountDown = 0.0

    // Virtual modifier key state
    var virtualModifier: CGEventFlags = CGEventFlags()
    
    // Python object pointer for "on_key()", "on_clipboard()"
    var keyboardCallback = PyObjectPtr()
    var clipboardCallback = PyObjectPtr()

    func TRACE(_ s: String) {
        #if DEBUG
        print(s)
        #endif
    }

    // For InputContext's exclusive control
    public func acquireLock() {
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        lock.lock()
    }
    
    // For InputContext's exclusive control
    public func releaseLock() {
        lock.unlock()
    }

    // Set/unset a Python callback function
    public func setCallback(name: String, callback: PyObjectPtr?){
        
        lock.lock()
        defer { lock.unlock() }

        if let callback = callback {
            switch name {
            case "Keyboard":
                self.setKeyboardCallback(callback: callback)
            case "Clipboard":
                self.setClipboardCallback(callback: callback)
            default:
                break
            }
        }
        else {
            switch name {
            case "Keyboard":
                self.unsetKeyboardCallback()
            case "Clipboard":
                self.unsetClipboardCallback()
            default:
                break
            }
        }
    }
    
    private func setKeyboardCallback(callback: PyObjectPtr) {
        self.keyboardCallback = callback
        self.keyboardCallback.IncRef()
    }
    
    private func unsetKeyboardCallback() {
        self.keyboardCallback.DecRef()
        self.keyboardCallback = PyObjectPtr()
    }
    
    private func setClipboardCallback(callback: PyObjectPtr) {
        self.clipboardCallback = callback
        self.clipboardCallback.IncRef()
    }
    
    private func unsetClipboardCallback() {
        self.clipboardCallback.DecRef()
        self.clipboardCallback = PyObjectPtr()
    }
    
    // Install keyboard hook to the OS
    public func installKeyboardHook() {

        lock.lock()
        defer { lock.unlock() }

        if self.eventSourceForTranslated != nil {
            print("Keyboard hook is already installed.")
            return
        }
        
        let eventMask = (1 << CGEventType.keyDown.rawValue) | (1 << CGEventType.keyUp.rawValue) | (1 << CGEventType.flagsChanged.rawValue)
        
        func _callback(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent, refcon: UnsafeMutableRawPointer?) -> Unmanaged<CGEvent>? {
            let hook = Unmanaged<Hook>.fromOpaque(refcon!).takeUnretainedValue()
            return hook.keyboardCallbackSwift(proxy: proxy, type: type, event: event)
        }
        
        self.eventTap = CGEvent.tapCreate(
            tap: CGEventTapLocation.cgSessionEventTap,
            place: CGEventTapPlacement.headInsertEventTap,
            options: CGEventTapOptions.defaultTap,
            eventsOfInterest: CGEventMask(eventMask),
            callback: _callback,
            userInfo: Unmanaged.passRetained(self).toOpaque()
        )
        
        if self.eventTap==nil {
            print("Failed to create event tap")
            return
        }
        
        self.runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, self.eventTap, 0)
        
        if self.runLoopSource==nil {
            print("Failed to create RunLoopSource")
            return
        }
        
        CFRunLoopAddSource(CFRunLoopGetCurrent(), self.runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: self.eventTap!, enable: true)
        
        self.eventSourceForTranslated = CGEventSource(stateID: CGEventSourceStateID.privateState)
        self.eventSourceForReplay = CGEventSource(stateID: CGEventSourceStateID.privateState)

        numPendingVirtualKeyEvents = 0
        deferredRealKeyEvents.removeAll()

        // start a common timer
        timer = Timer.scheduledTimer(withTimeInterval: Hook.timerInterval, repeats: true) { timer in
            self.onTimer()
        }
    }
    
    // Uninstall keyboard hook from the OS
    public func uninstallKeyboardHook() {
        
        lock.lock()
        defer { lock.unlock() }

        if self.eventSourceForTranslated == nil {
            print("Keyboard hook is not installed.")
            return
        }
        
        if let timer = self.timer {
            timer.invalidate()
            self.timer = nil
        }
        
        if let eventTap = self.eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
        }
        
        if let runLoopSource = self.runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, CFRunLoopMode.commonModes)
        }
        
        self.eventSourceForTranslated = nil
        self.eventSourceForReplay = nil
        self.runLoopSource = nil
        self.eventTap = nil
        
        numPendingVirtualKeyEvents = 0
        deferredRealKeyEvents.removeAll()
    }
    
    // Check if keyboard hook is successfully installed
    public func isKeyboardHookInstalled() -> Bool {
        return self.eventSourceForTranslated != nil
    }
    
    // Check if the keyboard hook is enabled (not disabled by the OS) and restore it as needed
    private func checkAndRestoreKeyboardHook() -> Bool {
        
        guard let eventTap = self.eventTap else {
            return false
        }
        
        if CGEvent.tapIsEnabled(tap: eventTap) {
            return false
        }
        
        numPendingVirtualKeyEvents = 0
        deferredRealKeyEvents.removeAll()
        
        CGEvent.tapEnable(tap: eventTap, enable: true)
        
        // Notify that hook restored
        if self.keyboardCallback.ptr() != nil {
            
            var gil = PyGIL(true);
            defer { gil.Release() }
            
            let json = """
            {"type": "hookRestored"}
            """
            
            var arg = PythonBridge.buildPythonString(json)
            var pyresult = PythonBridge.invokeCallable(self.keyboardCallback, arg)
            
            defer {
                arg.DecRef()
                pyresult.DecRef()
            }
            
            if pyresult.ptr() != nil && PythonBridge.parsePythonInt(pyresult) != 0 {
            }
        }
        
        return true
    }
    
    // Callback for keyboard hook
    private func keyboardCallbackSwift(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {

        lock.lock()
        defer { lock.unlock() }
        
        let keyCode = event.getIntegerValueField(.keyboardEventKeycode)
        
        let keyEventSource: KeyEventSource
        switch event.getIntegerValueField(.eventSourceStateID) {
        case Int64(eventSourceForTranslated!.sourceStateID.rawValue):
            keyEventSource = .translated
        case Int64(eventSourceForReplay!.sourceStateID.rawValue):
            keyEventSource = .replay
        default:
            keyEventSource = .real
        }
        
        TRACE("keyboardCallbackSwift(\(type), \(keyCode), \(keyEventSource))")
        
        // Event order handling:
        // Postpone real events if there are virtual key events pending or if there are preceeding postponed events
        if keyEventSource == .real {
            if numPendingVirtualKeyEvents > 0 || deferredRealKeyEvents.count > 0 {
                TRACE("keyboardCallbackSwift - defer real event \(numPendingVirtualKeyEvents), \(deferredRealKeyEvents.count)")
                deferredRealKeyEvents.append(event)
                return nil;
            }
        }
        
        process_event: do {
            // get event type - keyDown or keyUp
            let keyEventDirection: KeyEventDirection
            switch type {
            case .keyDown:
                keyEventDirection = .keyDown
                
            case .keyUp:
                keyEventDirection = .keyUp
                
            case .flagsChanged:
                
                // CapsLock key is special, skip processing
                if keyCode == VK.CAPITAL.rawValue {
                    break process_event
                }
                
                // Modifier flag to be updated by this key
                let changedFlags = keyCodeToEventFlags(keyCode: keyCode);
                
                // Flag changed for unknown reason, skip processing
                if changedFlags.isEmpty {
                    print("Flag changed for unknown reason - vk=\(keyCode)")
                    break process_event
                }
                
                // Distinguish keyDown or keyUp
                keyEventDirection = event.flags.intersection(changedFlags).isEmpty ? .keyUp : .keyDown
                
            default:
                print("Unexpected event type - \(type)")
                break process_event
            }
            
            if keyEventSource == .real || keyEventSource == .replay {
                if self.keyboardCallback.ptr() != nil {

                    var gil = PyGIL(true);
                    defer { gil.Release() }
                    
                    let json = """
                    {"type": "\(keyEventDirection)", "keyCode": \(keyCode)}
                    """
                    
                    var arg = PythonBridge.buildPythonString(json)
                    var pyresult = PythonBridge.invokeCallable(self.keyboardCallback, arg)
                    
                    defer {
                        arg.DecRef()
                        pyresult.DecRef()
                    }
                    
                    if pyresult.ptr() != nil && PythonBridge.parsePythonInt(pyresult) != 0 {
                        // Dispose event as it was processed in Python
                        event.type = .null
                        break process_event
                    }
                }
            }
            
            // For key events that were not processed in Python
            switch type {
            case .keyDown, .keyUp:
                // Overwrite modifier key flags
                event.flags = event.flags.subtracting(Hook.modifierFlags)
                event.flags = event.flags.union(virtualModifierStateToEventFlags(src: virtualModifier))
                
            case .flagsChanged:
                // Update virtual modifier state based on real modifier status change
                switch keyEventDirection {
                case .keyDown:
                    virtualModifier.insert(keyCodeToEventFlags(keyCode: keyCode))
                case .keyUp:
                    virtualModifier.remove(keyCodeToEventFlags(keyCode: keyCode))
                }
                
            default:
                break
            }
        }
        
        // Event order handling:
        // Process postponed real key events once all virtual key events are done
        if keyEventSource == .translated || keyEventSource == .replay {
            numPendingVirtualKeyEvents = max(numPendingVirtualKeyEvents-1, 0)
            if numPendingVirtualKeyEvents == 0 {
                flushRealKeyEvents()
            }
        }

        return Unmanaged.passUnretained(event)
    }
    
    // Multi-purpose timer for hook management
    private func onTimer() {

        lock.lock()
        defer { lock.unlock() }
        
        sanityCheckCountDown -= Hook.sanityCheckInterval
        if sanityCheckCountDown <= 0.0 {
            sanityCheckCountDown = Hook.timerInterval
            if checkAndRestoreKeyboardHook() {
                print("Re-enabled keyboard hook")
            }
        }

        if flushRealKeyEventsCountDown > 0.0 {
            flushRealKeyEventsCountDown -= Hook.timerInterval
            if flushRealKeyEventsCountDown <= 0 {
                flushRealKeyEvents()
            }
        }

        if Clipboard.changed {
            onClipboardChanged()
        }
    }
    
    private func onClipboardChanged() {
        if self.clipboardCallback.ptr() != nil {

            var gil = PyGIL(true);
            defer { gil.Release() }
            
            let json = "{}"
            
            var arg = PythonBridge.buildPythonString(json)
            var pyresult = PythonBridge.invokeCallable(self.clipboardCallback, arg)
            
            arg.DecRef()
            pyresult.DecRef()
        }
    }
    
    // Convert virtual modifier state to CoreGraphics's event flags
    private func virtualModifierStateToEventFlags(src: CGEventFlags) -> CGEventFlags
    {
        var dst = src
        
        if (src.rawValue & UInt64(NX_DEVICELCTLKEYMASK|NX_DEVICERCTLKEYMASK)) != 0 { dst.insert(.maskControl) }
        if (src.rawValue & UInt64(NX_DEVICELSHIFTKEYMASK|NX_DEVICERSHIFTKEYMASK)) != 0 { dst.insert(.maskShift) }
        if (src.rawValue & UInt64(NX_DEVICELALTKEYMASK|NX_DEVICERALTKEYMASK)) != 0 { dst.insert(.maskAlternate) }
        if (src.rawValue & UInt64(NX_DEVICELCMDKEYMASK|NX_DEVICERCMDKEYMASK)) != 0 { dst.insert(.maskCommand) }
        if (src.rawValue & UInt64(NX_SECONDARYFNMASK)) != 0 { dst.insert(.maskSecondaryFn) }
        
        return dst;
    }
    
    // Convert key code of modifier keys toCoreGraphics's event flags
    private func keyCodeToEventFlags( keyCode: Int64 ) -> CGEventFlags
    {
        switch(keyCode)
        {
        case 0x3B: // Left Control
            return CGEventFlags(rawValue: UInt64(NX_DEVICELCTLKEYMASK))
        case 0x3E: // Right Control
            return CGEventFlags(rawValue: UInt64(NX_DEVICERCTLKEYMASK))
        case 0x38: // Left Shift
            return CGEventFlags(rawValue: UInt64(NX_DEVICELSHIFTKEYMASK))
        case 0x3C: // Right Shift
            return CGEventFlags(rawValue: UInt64(NX_DEVICERSHIFTKEYMASK))
        case 0x37: // Left Command
            return CGEventFlags(rawValue: UInt64(NX_DEVICELCMDKEYMASK))
        case 0x36: // Right Command
            return CGEventFlags(rawValue: UInt64(NX_DEVICERCMDKEYMASK))
        case 0x3A: // Left Option
            return CGEventFlags(rawValue: UInt64(NX_DEVICELALTKEYMASK))
        case 0x3D: // Right Option
            return CGEventFlags(rawValue: UInt64(NX_DEVICERALTKEYMASK))
        case 0x3F: // Function
            return CGEventFlags(rawValue: UInt64(NX_SECONDARYFNMASK))
        case 0x39: // Caps Lock
            return CGEventFlags(rawValue: UInt64(NX_ALPHASHIFTMASK))
        default:
            return CGEventFlags(rawValue: 0)
        }
    }
    
    // Send a virtual key event
    public func sendKeyboardEvent(type: String, keyCode: Int, replay: Bool) {

        TRACE("sendKeyboardEvent(\(type), \(keyCode))")
        
        lock.lock()
        defer { lock.unlock() }

        let keyDown: Bool
        switch type {
        case "keyDown":
            keyDown = true
        case "keyUp":
            keyDown = false
        default:
            fatalError("Unknown keyboard event type: \(type)")
        }
        
        var eventSource: CGEventSource?
        if replay {
            eventSource = eventSourceForReplay
        } else {
            eventSource = eventSourceForTranslated
        }
        
        let event = CGEvent(keyboardEventSource: eventSource, virtualKey: CGKeyCode(keyCode), keyDown: keyDown)
        
        if let event = event {
            
            // Event order handling:
            // Count how many virtual key event are pending
            numPendingVirtualKeyEvents += 1
            
            // Event order handling:
            // Set timeout for postponed real key events
            flushRealKeyEventsCountDown = Hook.flushRealKeyEventsTimeout
            
            event.post(tap: CGEventTapLocation.cghidEventTap)
        }
    }
    
    // Event order handling:
    // Send all deferred real key events
    private func flushRealKeyEvents() {
        numPendingVirtualKeyEvents = 0
        if deferredRealKeyEvents.count > 0 {
            for event in deferredRealKeyEvents {
                event.post(tap: CGEventTapLocation.cghidEventTap)
            }
            deferredRealKeyEvents.removeAll()
        }
    }
    
    // Get keyboard layout ("ansi" / "jis" / "iso" / "unknown" )
    public func getKeyboardLayout() -> String {
        let physicalKeyboardLayoutType: Int = Int(KBGetLayoutType(Int16(LMGetKbdType())))
        switch physicalKeyboardLayoutType {
        case kKeyboardJIS:
            return "jis"
        case kKeyboardISO:
            return "iso"
        case kKeyboardANSI:
            return "ansi"
        default:
            return "unknown"
        }
    }
}
