//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-11.
//

import Foundation
import CoreGraphics

public enum EventType {
    case undefined
    case keyDown
    case keyUp
    case clipboardChanged
}

public class EventBase {
    var type : EventType = .undefined
    
    init(type: EventType) {
        self.type = type
    }
}

public class EventKeyDown : EventBase {
    var mod : Int = 0
    var vk : Int = 0
}

public class EventClipboard : EventBase {
    var s : String = ""
}

public class Hook {
    
    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var eventSource: CGEventSource?
    
    public init() {
        print("Hook.init()")
    }
    
    deinit {
        print("Hook.deinit()")
    }
    
    public func destroy() {
        print("Hook.destroy()")
    }
    
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
        print("Hook.setKeyboardCallback()")

        self.keyboardCallback = callback
        self.keyboardCallback.IncRef()

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
    
    public func unsetKeyboardCallback() {
        
        if let eventTap = self.eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
        }
        
        if let runLoopSource = self.runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, CFRunLoopMode.commonModes)
        }
        
        self.eventSource = nil
        self.runLoopSource = nil
        self.eventTap = nil

        self.keyboardCallback.DecRef()
        self.keyboardCallback = PyObjectPtr()
    }

    func keyboardCallbackSwift(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        
        if [CGEventType.keyDown, CGEventType.keyUp].contains(type) {
            
            let keyCode = event.getIntegerValueField(.keyboardEventKeycode)
            print( "EventType \(type), KeyCode \(keyCode)" )

            /*
            // Test swap A and B
            if keyCode == 0 {
                keyCode = 11
            } else if keyCode == 11 {
                keyCode = 0
            }
            event.setIntegerValueField(.keyboardEventKeycode, value: keyCode)
            */
            
            if let pythonBridge = PythonBridge.getInstance() {
                var arg = PyObjectPtr()
                pythonBridge.invokeCallable(self.keyboardCallback, arg)
            }
        }
        return Unmanaged.passUnretained(event)
    }

    func sendKey() {
        
        let keydown_event = CGEvent(keyboardEventSource: eventSource, virtualKey: 179, keyDown: true)!
        let keyup_event = CGEvent(keyboardEventSource: eventSource, virtualKey: 179, keyDown: false)!
        
        keydown_event.post(tap: CGEventTapLocation.cghidEventTap)
        keyup_event.post(tap: CGEventTapLocation.cghidEventTap)
    }

}
