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

public enum UIValueType {
    case uiElement
    case bool
    case number
    case string
    case range
    case point
    case size
    case rect
    case array
    case unknown
}

public struct UIValue {
    
    private var value: AnyObject?
    
    public init() {
    }
    
    public init(_ value: AnyObject) {
        self.value = value
    }
    
    public func getType() -> UIValueType {
        
        guard let value else { return .unknown }
        
        let type = CFGetTypeID(value)
        switch type {
        case CFNumberGetTypeID():
            return .number
        case CFBooleanGetTypeID():
            return .bool
        case CFStringGetTypeID():
            return .string
        case AXUIElementGetTypeID():
            return .uiElement
        case AXValueGetTypeID():
            let type = AXValueGetType(value as! AXValue)
            switch type {
            case .cfRange:
                return .range
            case .cgPoint:
                return .point
            case .cgSize:
                return .size
            case .cgRect:
                return .rect
            default:
                return .unknown
            }
        case CFArrayGetTypeID():
            return .array
        default:
            return .unknown
        }
    }
    
    public func getValueBool() -> Bool {
        guard let value else { return false }
        return value as! Bool
    }
    
    public func getValueNumber() -> Int {
        guard let value else { return 0 }
        return value as! Int
    }
    
    public func getValueString() -> String {
        guard let value else { return "" }
        var s = value as! String
        
        // Workaround for https://github.com/swiftlang/swift/issues/69870
        s.makeContiguousUTF8()
        
        return s
    }
    
    public func getValueRect() -> [Float] {
        var rect: CGRect = CGRect.zero
        guard let value else { return [0,0,0,0] }
        AXValueGetValue(value as! AXValue, .cgRect, &rect)
        return [Float(rect.origin.x), Float(rect.origin.y), Float(rect.size.width), Float(rect.size.height)]
    }
    
    public func getValueUIElement() -> UIElement {
        guard let value else { return UIElement() }
        return UIElement( value as! AXUIElement )
    }
    
    public func getValueArray() -> [UIValue] {
        guard let value else { return [] }
        //return value as! [UIValue]
        
        let array = value as! [AnyObject]
        return array.map { UIValue($0) }
    }
    
}

public class UIElement {
        
    var elm: AXUIElement?
    
    public init() {
        //print("UIElement.init()")
    }
    
    init(_ elm: AXUIElement) {
        //print("UIElement.init()")
        self.elm = elm
    }
    
    deinit {
        //print("UIElement.deinit()")
    }

    public static func getSystemWideElement() -> UIElement {
        let elm: AXUIElement = AXUIElementCreateSystemWide()
        return UIElement(elm)
    }
    
    public func getAttributeNames() -> [String] {
        
        guard let elm else {
            return []
        }
        
        var names: CFArray?
        let result = AXUIElementCopyAttributeNames(elm, &names)
        if result != .success {
            return []
        }

        return names! as [AnyObject] as! [String]
    }
    
    public func getAttributeValue(name: String) -> UIValue? {
        
        if name == "AXCustomRotors" {
            
        }
        
        guard let elm else {
            return nil
        }
        
        var value: AnyObject?
        AXUIElementCopyAttributeValue(elm, name as CFString, &value)
        
        guard let value else {
            return nil
        }

        return UIValue(value)

        /*
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
        */
    }

    /*
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
    */
    
    func getParent() -> AXUIElement? {
        let parent = getAttributeValue(name: "AXParent") as! AXUIElement?
        return parent
    }

    /*
    public func getFocusedChild() -> AXUIElement? {
        
        let role = getAttributeValue(elm: self.elm, name: "AXRole") as! String
        switch role {
        case "AXSystemWide":
            return getAttributeValue(elm: self.elm, name: "AXFocusedApplication") as! AXUIElement?
        case "AXApplication":
            return getAttributeValue(elm: self.elm, name: "AXFocusedWindow") as! AXUIElement?
        default:
            return nil
        }
    }
    */
    
    /*
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
    */
}

