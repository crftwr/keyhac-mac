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

    /*
    NX_DEVICELCTLKEYMASK:   0x00000001
    NX_DEVICERCTLKEYMASK:   0x00002000
    NX_COMMANDMASK:         0x00100000
    NX_DEVICELSHIFTKEYMASK: 0x00000002
    NX_DEVICERSHIFTKEYMASK: 0x00000004
    NX_SHIFTMASK:           0x00020000
    NX_DEVICELALTKEYMASK:   0x00000020
    NX_DEVICERALTKEYMASK:   0x00000040
    NX_ALTERNATEMASK:       0x00080000
    NX_DEVICELCMDKEYMASK:   0x00000008
    NX_DEVICERCMDKEYMASK:   0x00000010
    NX_COMMANDMASK:         0x00100000
    NX_SECONDARYFNMASK:     0x00800000
    NX_ALPHASHIFTMASK:      0x00010000
    */
    
    enum KeyEventDirection {
        case keyDown
        case keyUp
    }
    
    enum KeyEventSource {
        case real
        case virtual
    }
    
    // Keyboard hook at OS level
    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var eventSource: CGEventSource?
    var sanityCheckTimer: Timer?
    
    // Event oder handling
    var numPendingVirtualKeyEvents: Int = 0
    var deferredRealKeyEvents: [CGEvent] = []
    
    // Virtual modifier key state
    var virtualModifier: CGEventFlags = CGEventFlags()

    // Python object pointer for "on_key()"
    var keyboardCallback = PyObjectPtr()
    
    func TRACE(_ s: String) {
        #if DEBUG
        print(s)
        #endif
    }
    
    public func setCallback(name: String, callback: PyObjectPtr?){
        
        if let callback = callback {
            switch name {
            case "Keyboard":
                self.setKeyboardCallback(callback: callback)
            default:
                break
            }
        }
        else {
            switch name {
            case "Keyboard":
                self.unsetKeyboardCallback()
            default:
                break
            }
        }
    }

    public func setKeyboardCallback(callback: PyObjectPtr) {
        self.keyboardCallback = callback
        self.keyboardCallback.IncRef()
    }
    
    public func unsetKeyboardCallback() {
        self.keyboardCallback.DecRef()
        self.keyboardCallback = PyObjectPtr()
    }

    public func installKeyboardHook() {
        
        if self.eventSource != nil {
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
        
        // start a timer to check and restore keyboard hook
        sanityCheckTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
            if self.checkAndRestoreKeyboardHook() {
                print("Re-enabled keyboard hook")
            }
        }
        
        self.eventSource = CGEventSource(stateID: CGEventSourceStateID.privateState)
        
        numPendingVirtualKeyEvents = 0
        deferredRealKeyEvents.removeAll()
    }
    
    public func uninstallKeyboardHook() {
        
        if self.eventSource == nil {
            print("Keyboard hook is not installed.")
            return
        }
        
        if let sanityCheckTimer = self.sanityCheckTimer {
            sanityCheckTimer.invalidate()
            self.sanityCheckTimer = nil
        }
        
        if let eventTap = self.eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
        }
        
        if let runLoopSource = self.runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, CFRunLoopMode.commonModes)
        }
        
        self.eventSource = nil
        self.runLoopSource = nil
        self.eventTap = nil

        numPendingVirtualKeyEvents = 0
        deferredRealKeyEvents.removeAll()
    }
    
    public func isKeyboardHookInstalled() -> Bool {
        return self.eventSource != nil
    }
    
    public func checkAndRestoreKeyboardHook() -> Bool {
        
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
    
    func keyboardCallbackSwift(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        
        var gil = PyGIL(true);
        defer { gil.Release() }
        
        let keyCode = event.getIntegerValueField(.keyboardEventKeycode)
        
        let keyEventSource: KeyEventSource
        if event.getIntegerValueField(.eventSourceStateID) == eventSource!.sourceStateID.rawValue {
            keyEventSource = .virtual
        }
        else {
            keyEventSource = .real
        }
        
        TRACE("keyboardCallbackSwift(\(type), \(keyCode), \(keyEventSource))")
        
        // Event oder handling:
        // Postpone real events if there are virtual key events pending or if there are preceeding postponed events
        if keyEventSource == .real {
            if numPendingVirtualKeyEvents > 0 || deferredRealKeyEvents.count > 0 {
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
            
            if keyEventSource == .real {
                if self.keyboardCallback.ptr() != nil {
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

        // Event oder handling:
        // Process postponed real key events once all virtual key events are done
        if keyEventSource == .virtual {
            assert(numPendingVirtualKeyEvents > 0)
            numPendingVirtualKeyEvents -= 1
            if numPendingVirtualKeyEvents == 0 && deferredRealKeyEvents.count > 0 {
                for event in deferredRealKeyEvents {
                    event.post(tap: CGEventTapLocation.cghidEventTap)
                }
                deferredRealKeyEvents.removeAll()
            }
        }
        
        return Unmanaged.passUnretained(event)
    }
    
    func virtualModifierStateToEventFlags(src: CGEventFlags) -> CGEventFlags
    {
        var dst = src
        
        if (src.rawValue & UInt64(NX_DEVICELCTLKEYMASK|NX_DEVICERCTLKEYMASK)) != 0 { dst.insert(.maskControl) }
        if (src.rawValue & UInt64(NX_DEVICELSHIFTKEYMASK|NX_DEVICERSHIFTKEYMASK)) != 0 { dst.insert(.maskShift) }
        if (src.rawValue & UInt64(NX_DEVICELALTKEYMASK|NX_DEVICERALTKEYMASK)) != 0 { dst.insert(.maskAlternate) }
        if (src.rawValue & UInt64(NX_DEVICELCMDKEYMASK|NX_DEVICERCMDKEYMASK)) != 0 { dst.insert(.maskCommand) }
        if (src.rawValue & UInt64(NX_SECONDARYFNMASK)) != 0 { dst.insert(.maskSecondaryFn) }
        
        return dst;
    }

    func keyCodeToEventFlags( keyCode: Int64 ) -> CGEventFlags
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

    public func sendKeyboardEvent(type: String, keyCode: Int) {
        
        TRACE("sendKeyboardEvent(\(type), \(keyCode))")
        
        let keyDown: Bool
        switch type {
        case "keyDown":
            keyDown = true
        case "keyUp":
            keyDown = false
        default:
            fatalError("Unknown keyboard event type: \(type)")
        }
        
        let event = CGEvent(keyboardEventSource: eventSource, virtualKey: CGKeyCode(keyCode), keyDown: keyDown)
        
        if let event = event {

            // Event oder handling:
            // Count how many virtual key event are pending
            numPendingVirtualKeyEvents += 1

            event.post(tap: CGEventTapLocation.cghidEventTap)
        }
    }
    
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
