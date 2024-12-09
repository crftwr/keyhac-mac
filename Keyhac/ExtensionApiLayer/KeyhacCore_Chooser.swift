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
    let uuid: String
    
    public init(icon: String, text: String, uuid: String) {
        self.icon = icon
        self.text = text
        self.uuid = uuid
    }
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
    
    init( name: String, items: [ChooserItem], onSelectedCallback: PyObjectPtr, onCanceledCallback: PyObjectPtr ) {
        
        self.name = name
        
        self.items = items
        
        self.onSelectedCallback = onSelectedCallback
        self.onSelectedCallback.IncRef()
        
        self.onCanceledCallback = onCanceledCallback
        self.onCanceledCallback.IncRef()
    }
    
    deinit {
        self.destroy()
    }
    
    public static func open( name: String, items: [ChooserItem], onSelectedCallback: PyObjectPtr, onCanceledCallback: PyObjectPtr ) -> Chooser {
        
        if let existingChooser = getInstance(name: name) {
            existingChooser.destroy()
        }
        
        let chooser = Chooser( name: name, items: items, onSelectedCallback: onSelectedCallback, onCanceledCallback: onCanceledCallback )
        instances[name] = chooser
        
        if let url = URL(string: "keyhac://chooser/\(name)") {
            NSWorkspace.shared.open(url)
        }
        
        return chooser
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
    
    public func onSelected(uuid: String) {
        
        if self.onSelectedCallback.ptr() != nil {
            
            var gil = PyGIL(true);
            defer { gil.Release() }
            
            let json = """
            {"uuid": "\(uuid)"}
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
