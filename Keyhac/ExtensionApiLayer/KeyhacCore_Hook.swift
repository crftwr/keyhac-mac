//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-11.
//

import Foundation
import CoreGraphics

public class Hook {

    private static let instance = Hook()
    public static func getInstance() -> Hook { return instance }

    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var eventSource: CGEventSource?
    
    var modifier: CGEventFlags = CGEventFlags()
    var keyboardCallback = PyObjectPtr()
    
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
        
        self.eventSource = CGEventSource(stateID: CGEventSourceStateID.privateState)
    }
    
    public func uninstallKeyboardHook() {
        
        if self.eventSource == nil {
            print("Keyboard hook is not installed.")
            return
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
    }
    
    func keyboardCallbackSwift(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        
        foo: do {
        
            let keyCode = event.getIntegerValueField(.keyboardEventKeycode)

            let typeString: String
            switch type {
            case .keyDown: typeString = "keyDown"
            case .keyUp: typeString = "keyUp"
            case .flagsChanged:
                let flags = event.flags
                let changed_flags = keyCodeToFlag(keyCode: keyCode);

                if changed_flags.isEmpty {
                    // FIXME : 普通のモディファイアキー以外の理由で kCGEventFlagsChanged
                    // が来たときも、modifier を更新するべき
                    
                    break foo
                }
                
                typeString = flags.intersection(changed_flags).isEmpty ? "keyUp" : "keyDown"
            default: typeString = "unknown"
            }
            
            // 自分で挿入したイベントはスクリプト処理しない
            let injected_by_self = event.getIntegerValueField(.eventSourceStateID) == eventSource!.sourceStateID.rawValue
            
            if !injected_by_self {
                
                if self.keyboardCallback.ptr() != nil {
                    let json = """
                    {"type": "\(typeString)", "keyCode": \(keyCode)}
                    """

                    var arg = PythonBridge.buildPythonString(json)
                    var pyresult = PythonBridge.invokeCallable(self.keyboardCallback, arg)
                    
                    defer {
                        arg.DecRef()
                        pyresult.DecRef()
                    }
                    
                    if pyresult.ptr() != nil && PythonBridge.parsePythonInt(pyresult) != 0 {
                        // Python側で処理済みなのでイベントを捨てる
                        event.type = .null
                        break foo
                    }
                }
            }

            // Pythonで処理されなかったキーに対してはモディファイアキーの処理を行う
            switch type {
            case .keyDown, .keyUp:
                // 仮想のモディファイアキーの状態をイベントに設定する
                event.flags = fixupEventFlagMask(src: modifier)
                    
            case .flagsChanged:
                // 仮想のモディファイア状態を更新する
                if typeString == "keyDown" {
                    modifier.insert(keyCodeToFlag(keyCode: keyCode))
                }
                else {
                    modifier.remove(keyCodeToFlag(keyCode: keyCode))
                }

            default:
                break
            }
        }
        return Unmanaged.passUnretained(event)
    }
    
    func fixupEventFlagMask(src: CGEventFlags) -> CGEventFlags
    {
        var dst = src
        
        if (src.rawValue & UInt64(NX_DEVICELCTLKEYMASK|NX_DEVICERCTLKEYMASK)) != 0 { dst.insert(.maskControl) }
        if (src.rawValue & UInt64(NX_DEVICELSHIFTKEYMASK|NX_DEVICERSHIFTKEYMASK)) != 0 { dst.insert(.maskShift) }
        if (src.rawValue & UInt64(NX_DEVICELALTKEYMASK|NX_DEVICERALTKEYMASK)) != 0 { dst.insert(.maskAlternate) }
        if (src.rawValue & UInt64(NX_DEVICELCMDKEYMASK|NX_DEVICERCMDKEYMASK)) != 0 { dst.insert(.maskCommand) }
        if (src.rawValue & UInt64(NX_SECONDARYFNMASK)) != 0 { dst.insert(.maskSecondaryFn) }
        
        return dst;
    }

    func keyCodeToFlag( keyCode: Int64 ) -> CGEventFlags
    {
        switch(keyCode)
        {
        case 0x3B: // kVK_Control
            return CGEventFlags(rawValue: UInt64(NX_DEVICELCTLKEYMASK))
        case 0x3E: // kVK_RightControl
            return CGEventFlags(rawValue: UInt64(NX_DEVICERCTLKEYMASK))
        case 0x38: // kVK_Shift
            return CGEventFlags(rawValue: UInt64(NX_DEVICELSHIFTKEYMASK))
        case 0x3C: // kVK_RightShift
            return CGEventFlags(rawValue: UInt64(NX_DEVICERSHIFTKEYMASK))
        case 0x37: // kVK_Command
            return CGEventFlags(rawValue: UInt64(NX_DEVICELCMDKEYMASK))
        case 0x36: // kVK_RightCommand
            return CGEventFlags(rawValue: UInt64(NX_DEVICERCMDKEYMASK))
        case 0x3A: // kVK_Option
            return CGEventFlags(rawValue: UInt64(NX_DEVICELALTKEYMASK))
        case 0x3D: // kVK_RightOption
            return CGEventFlags(rawValue: UInt64(NX_DEVICERALTKEYMASK))
        case 0x3F: // kVK_Function
            return CGEventFlags(rawValue: UInt64(NX_SECONDARYFNMASK))
        default:
            return CGEventFlags(rawValue: 0)
        }
    }

    /*
    func lookupKeyState( const KeyMap & keys, vk: Int ) -> Bool {
        // GetKeys / KeyMap では、左右のモディファイアキーの区別がつかないので、
        // どちらかが押されていたら、両方押されているとみなす。
        switch(vk)
        {
        case kVK_RightControl:
            vk = kVK_Control;
            break;
            
        case kVK_RightShift:
            vk = kVK_Shift;
            break;
            
        case kVK_RightCommand:
            vk = kVK_Command;
            break;
            
        case kVK_RightOption:
            vk = kVK_Option;
            break;
            
        default:
            break;
        }
        
        return (keys[ vk / 32 ].bigEndianValue & (1<<(vk%32))) != 0;
    }
    */

    public func fixWierdModifierState() {
        
        /*
        KeyMap keys;
        getKeys(keys);
        
        if( ! LookupKeyState(keys,kVK_Control) )
        {
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_Control) );
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_RightControl) );
        }
        
        if( ! LookupKeyState(keys,kVK_Shift) )
        {
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_Shift) );
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_RightShift) );
        }
        
        if( ! LookupKeyState(keys,kVK_Command) )
        {
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_Command) );
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_RightCommand) );
        }
        
        if( ! LookupKeyState(keys,kVK_Option) )
        {
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_Option) );
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_RightOption) );
        }
        
        if( ! LookupKeyState(keys,kVK_Function) )
        {
            modifier = (CGEventFlags)( modifier & ~VkToFlag(kVK_Function) );
        }
        */
    }

    public func sendKeyboardEvent(type: String, keyCode: Int) {
        
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
            event.post(tap: CGEventTapLocation.cghidEventTap)
        }
    }

}
