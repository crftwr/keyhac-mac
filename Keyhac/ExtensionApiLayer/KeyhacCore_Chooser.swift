//
//  KeyhacCore_Chooser.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import Foundation
import SwiftUI

public struct ChooserItem {
    let icon: String
    let text: String
    let uuid: String = UUID().uuidString
    
    public init(icon: String, text: String) {
        self.icon = icon
        self.text = text
    }
}

public enum ModifierFlags: Int {
    case MODKEY_ALT   = 0x00000001
    case MODKEY_CTRL  = 0x00000002
    case MODKEY_SHIFT = 0x00000004
    case MODKEY_WIN   = 0x00000008
    case MODKEY_CMD   = 0x00000010
    case MODKEY_FN    = 0x00000020
    case MODKEY_USER0 = 0x00000040
    case MODKEY_USER1 = 0x00000080
}

public class Chooser {
    
    private static var instances: [String : Chooser] = [:]
    public static func getInstance(name: String) -> Chooser? {
        return instances[name]
    }
    
    var name: String
    var items: [ChooserItem]
    var onSelectedCallback: PyObjectPtr
    var onCanceledCallback: PyObjectPtr
    
    public init( name: String, items: [ChooserItem], onSelectedCallback: PyObjectPtr, onCanceledCallback: PyObjectPtr ) {
        
        if let existingChooser = Chooser.getInstance(name: name) {
            existingChooser.destroy()
        }
        
        self.name = name
        
        self.items = items
        
        self.onSelectedCallback = onSelectedCallback
        self.onSelectedCallback.IncRef()
        
        self.onCanceledCallback = onCanceledCallback
        self.onCanceledCallback.IncRef()

        Chooser.instances[name] = self
    }
    
    deinit {
        self.destroy()
    }
    
    public func open( x: Int, y: Int, width: Int, height: Int ) {
        if let url = URL(string: "keyhac://chooser/\(name)?x=\(x)&y=\(y)&width=\(width)&height=\(height)") {
            NSWorkspace.shared.open(url)
        }
    }
    
    public func destroy() {
        
        var gil = PyGIL(true);
        defer { gil.Release() }

        self.items.removeAll()
        
        self.onSelectedCallback.DecRef()
        self.onSelectedCallback = PyObjectPtr()
        
        self.onCanceledCallback.DecRef()
        self.onCanceledCallback = PyObjectPtr()
    }
    
    public func onSelected(uuid: String, nsModifierFlags: NSEvent.ModifierFlags) {
        
        if self.onSelectedCallback.ptr() != nil {
            
            var gil = PyGIL(true);
            defer { gil.Release() }
            
            var foundIndex: Int = -1
            for (index, item) in self.items.enumerated() {
                if item.uuid == uuid {
                    foundIndex = index
                    break
                }
            }
            
            if foundIndex < 0 {
                return
            }
            
            var modifierFlags = 0
            if nsModifierFlags.contains(.shift) {modifierFlags |= ModifierFlags.MODKEY_SHIFT.rawValue}
            if nsModifierFlags.contains(.control) {modifierFlags |= ModifierFlags.MODKEY_CTRL.rawValue}
            if nsModifierFlags.contains(.option) {modifierFlags |= ModifierFlags.MODKEY_ALT.rawValue}
            if nsModifierFlags.contains(.command) {modifierFlags |= ModifierFlags.MODKEY_CMD.rawValue}
            
            let json = """
            {"index": "\(foundIndex)", "modifierFlags": "\(modifierFlags)"}
            """
            
            var arg = PythonBridge.buildPythonString(json)
            var pyresult = PythonBridge.invokeCallable(self.onSelectedCallback, arg)
            
            arg.DecRef()
            pyresult.DecRef()
        }
        
        destroy()
    }
    
    public func onCanceled() {

        if self.onCanceledCallback.ptr() != nil {
            
            var gil = PyGIL(true);
            defer { gil.Release() }
            
            let json = "{}"
            
            var arg = PythonBridge.buildPythonString(json)
            var pyresult = PythonBridge.invokeCallable(self.onCanceledCallback, arg)
            
            arg.DecRef()
            pyresult.DecRef()
        }

        destroy()
    }
}
