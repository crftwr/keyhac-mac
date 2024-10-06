//
//  KeyboardHook.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import Foundation
import CoreGraphics

class KeyboardHook {
    
    static let instance = KeyboardHook()
    
    var installed: Bool = false
    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var eventSource: CGEventSource?

    func install() -> Bool {
        
        if self.installed {
            print("KeyboardHook is already installed.")
            return true;
        }
        
        print("Installing KeyboardHook")
        
        let eventMask = (1 << CGEventType.keyDown.rawValue) | (1 << CGEventType.keyUp.rawValue) | (1 << CGEventType.flagsChanged.rawValue)
        
        func _callback(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent, refcon: UnsafeMutableRawPointer?) -> Unmanaged<CGEvent>? {
            let keyboard_hook = Unmanaged<KeyboardHook>.fromOpaque(refcon!).takeUnretainedValue()
            return keyboard_hook.callback(proxy: proxy, type: type, event: event)
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
            return false
        }
        
        self.runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, self.eventTap, 0)

        if self.runLoopSource==nil {
            print("Failed to create RunLoopSource")
            return false
        }

        CFRunLoopAddSource(CFRunLoopGetCurrent(), self.runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: self.eventTap!, enable: true)
        
        self.eventSource = CGEventSource(stateID: CGEventSourceStateID.privateState)
        
        self.installed = true
        
        print("KeyboardHook installation successful")

        return true
    }
    
    func uninstall() -> Bool {

        if !self.installed {
            print("KeyboardHook is not installed.")
            return true;
        }
        
        print("Uninstalling KeyboardHook")

        if let eventTap = self.eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
        }

        if let runLoopSource = self.runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, CFRunLoopMode.commonModes)
        }

        self.eventSource = nil
        self.runLoopSource = nil
        self.eventTap = nil

        self.installed = false
        
        print("KeyboardHook uninstallation successful")

        return true
    }

    func callback(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        
        if [CGEventType.keyDown, CGEventType.keyUp].contains(type) {
            
            var keyCode = event.getIntegerValueField(.keyboardEventKeycode)
            print( "EventType \(type), KeyCode \(keyCode)" )

            // Test swap A and B
            if keyCode == 0 {
                keyCode = 11
            } else if keyCode == 11 {
                keyCode = 0
            }
            event.setIntegerValueField(.keyboardEventKeycode, value: keyCode)
        }
        return Unmanaged.passUnretained(event)
    }
    
    func sendKey() {
        
        let keydown_event = CGEvent(keyboardEventSource: eventSource, virtualKey: 179, keyDown: true)!
        let keyup_event = CGEvent(keyboardEventSource: eventSource, virtualKey: 179, keyDown: false)!
        
        keydown_event.post(tap: CGEventTapLocation.cghidEventTap)
        keyup_event.post(tap: CGEventTapLocation.cghidEventTap)
    }
    
    func test1(){
        PythonBridge.getInstance().pointee.callFunction()
    }
}
