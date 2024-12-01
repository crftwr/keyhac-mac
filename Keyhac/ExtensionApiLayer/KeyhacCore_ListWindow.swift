//
//  KeyhacCore_Clipboard.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import Foundation
import SwiftUI

public class ListWindow {
    
    @Environment(\.openWindow) static private var openWindow
    @Environment(\.dismissWindow) static private var dismissWindow

    private static var instances: [String : ListWindow] = [:]
    public static func getInstance(name: String) -> ListWindow? {
        return instances[name]
    }
    
    var name: String
    var items: [ListWindowItem]
    var onSelectedCallback: PyObjectPtr
    var onCanceledCallback: PyObjectPtr
    
    init( name: String, items: [ListWindowItem], onSelectedCallback: PyObjectPtr, onCanceledCallback: PyObjectPtr ) {
        
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
    
    public static func open( name: String, items: [ListWindowItem], onSelectedCallback: PyObjectPtr, onCanceledCallback: PyObjectPtr ) -> ListWindow {
        
        if let existingListWindow = getInstance(name: name) {
            existingListWindow.destroy()
        }
        
        let listWindow = ListWindow( name: name, items: items, onSelectedCallback: onSelectedCallback, onCanceledCallback: onCanceledCallback )
        instances[name] = listWindow
        
        openWindow(id: "list", value: name)
        NSApp.activate()
        
        return listWindow
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
        
        ListWindow.dismissWindow(id: "list", value: name)
        
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

        ListWindow.dismissWindow(id: "list", value: name)

        destroy()
    }
}
