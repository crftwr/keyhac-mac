//
//  KeyhacCore_Clipboard.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import Foundation
import AppKit

public class Clipboard {
    
    private static let lock = NSRecursiveLock()
    
    static var previousChangeCount: NSInteger = 0
    
    var items: [NSPasteboardItem] = []
    
    public init() {
    }
    
    private init(src: [NSPasteboardItem]) {
        items = Clipboard.copyItems(src: src)
    }
    
    deinit {
    }
    
    public func destroy() {
        items = []
    }
    
    public static var changed: Bool {
        
        lock.lock()
        defer { lock.unlock() }

        let changeCount = NSPasteboard.general.changeCount
        
        if Clipboard.previousChangeCount != changeCount {
            Clipboard.previousChangeCount = changeCount
            return true
        }

        return false
    }
    
    public static func getCurrent() -> Clipboard {
        
        lock.lock()
        defer { lock.unlock() }

        if let items = NSPasteboard.general.pasteboardItems {
            let c = Clipboard(src: items)
            return c
        }
        
        return Clipboard()
    }
    
    public static func setCurrent(src: Clipboard) {
        
        lock.lock()
        defer { lock.unlock() }

        // Don't detect clipboard change by self
        Clipboard.previousChangeCount += 1
        
        NSPasteboard.general.clearContents()
        NSPasteboard.general.writeObjects(copyItems(src: src.items))
    }
    
    static func copyItems( src: [NSPasteboardItem] ) -> [NSPasteboardItem] {
        
        var dst: [NSPasteboardItem] = []
        
        for srcItem in src {
            let item = NSPasteboardItem()
            
            for type in srcItem.types {
                if let data = srcItem.data(forType: type) {
                    item.setData(data, forType: type)
                }
            }
            
            dst.append(item)
        }
        
        return dst
    }
    
    public func getString() -> String? {
        
        let s = items.first?.string(forType: .string)
        guard var s = s else { return nil }

        // Workaround for https://github.com/swiftlang/swift/issues/69870
        s.makeContiguousUTF8()

        return s
    }
}
