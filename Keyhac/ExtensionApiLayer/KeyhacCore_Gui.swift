//
//  KeyhacCore_Gui.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-19.
//

import Foundation
import CoreGraphics
import AppKit
import Cocoa

public class Gui {
        
    static func getAttributeValue(elm: AXUIElement, name: String) -> Any? {

        var value: AnyObject?
        AXUIElementCopyAttributeValue(elm, name as CFString, &value)
        
        if let value = value {
            let type = CFGetTypeID(value)
            switch type {
            case AXUIElementGetTypeID():
                return value as! AXUIElement
            case AXValueGetTypeID():
                let type = AXValueGetType(value as! AXValue)
                switch type {
                case .cgSize:
                    var axvalue: CGSize = CGSize.zero
                    AXValueGetValue(value as! AXValue, type, &axvalue)
                    return axvalue
                default:
                    print("AXValueType: \(type)")
                    return value
                }
            case CFBooleanGetTypeID():
                return value as! Bool
            case CFStringGetTypeID():
                return value as! String
            default:
                print("CFTypeID: \(type)")
                return value
            }
        }
        else {
            return nil
        }
    }
    
    static func printDetails(elm: AXUIElement) {
        
        var result: AXError
        
        print("Elm: \(elm)")
        
        var names: CFArray?
        result = AXUIElementCopyAttributeNames(elm, &names)
        if result != .success {
            print("  AXUIElementCopyAttributeNames failed: \(result)")
            return
        }
        if result == .success {
            let names = names! as [AnyObject] as! [String]
            
            for name in names {
                let value = getAttributeValue(elm:elm, name:name)
                if let value = value {
                    print("  Attr \(name): \(value)")
                }
                else {
                    print("  Attr \(name): nil")
                }
            }
        }
    }
    
    static func getParent(elm: AXUIElement) -> AXUIElement? {
        let parent = getAttributeValue(elm: elm, name: "AXParent") as! AXUIElement?
        return parent
    }
    
    static func getFocusedChild(elm: AXUIElement) -> AXUIElement? {
        
        let role = getAttributeValue(elm: elm, name: "AXRole") as! String
        switch role {
        case "AXSystemWide":
            return getAttributeValue(elm: elm, name: "AXFocusedApplication") as! AXUIElement?
        case "AXApplication":
            return getAttributeValue(elm: elm, name: "AXFocusedWindow") as! AXUIElement?
        default:
            return nil
        }
    }
    
    public static func getFocus() -> String {
        
        var elm: AXUIElement? = AXUIElementCreateSystemWide()
            
        /*
        // from top to bottom
        while elm != nil {
            printDetails(elm: elm!)
            print("------------")
            
            elm = getFocusedChild(elm: elm!)
        }
        */
        
        // from bottom to top
        elm = getAttributeValue(elm: elm!, name: "AXFocusedUIElement") as! AXUIElement?
        while elm != nil {
            printDetails(elm: elm!)
            print("------------")

            elm = getParent(elm: elm!)
        }
        
        return "Hello"
    }
}

