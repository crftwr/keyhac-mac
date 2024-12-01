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

    private static var instances: [String : ListWindow] = [:]
    public static func getInstance(name: String) -> ListWindow? {
        return instances[name]
    }
    
    var items: [ListWindowItem]
    var onSelected: PyObjectPtr
    var onCanceled: PyObjectPtr

    init( items: [ListWindowItem], onSelected: PyObjectPtr, onCanceled: PyObjectPtr ) {
        
        self.items = items
        
        self.onSelected = onSelected
        self.onSelected.IncRef()

        self.onCanceled = onCanceled        
        self.onCanceled.IncRef()
    }
    
    deinit {
        self.destroy()
    }
    
    public static func open( name: String, items: [ListWindowItem], onSelected: PyObjectPtr, onCanceled: PyObjectPtr ) -> ListWindow {
        
        if let existingListWindow = getInstance(name: name) {
            existingListWindow.destroy()
        }

        let listWindow = ListWindow( items: items, onSelected: onSelected, onCanceled: onCanceled )
        instances[name] = listWindow
        
        openWindow(id: "list", value: name)
        NSApp.activate()

        return listWindow
    }
    
    public func destroy() {
        
        self.onSelected.DecRef()
        self.onSelected = PyObjectPtr()
        
        self.onCanceled.DecRef()
        self.onCanceled = PyObjectPtr()
    }
}
