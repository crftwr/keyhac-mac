//
//  KeyhacCore_Clipboard.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import Foundation
import Cocoa

public class Clipboard {
    
    private static let instance = Clipboard()
    public static func getInstance() -> Clipboard { return instance }
    
    var changeCount: NSInteger = 0
    
    public var changed: Bool {
        let newCount = NSPasteboard.general.changeCount
        
        if self.changeCount != newCount {
            self.changeCount = newCount
            return true
        }

        return false
    }
    
    public func get() -> String {
        if let s = NSPasteboard.general.string(forType: .string) {
            return s
        }
        return ""
    }
}
