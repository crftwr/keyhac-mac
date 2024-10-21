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
    case dictionary
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
        case CFDictionaryGetTypeID():
            return .dictionary
        default:
            let unsupportedTypeDesc = CFCopyTypeIDDescription(type)
            print("Unsupported type: \(unsupportedTypeDesc!)")
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
    
    public func getValueRange() -> [Int] {
        var range: CFRange = CFRange.init(location:0, length:0)
        guard let value else { return [0,0] }
        AXValueGetValue(value as! AXValue, .cfRange, &range)
        return [range.location, range.length]
    }
    
    public func getValuePoint() -> [Float] {
        var point: CGPoint = CGPoint.zero
        guard let value else { return [0,0] }
        AXValueGetValue(value as! AXValue, .cgPoint, &point)
        return [Float(point.x), Float(point.y)]
    }
    
    public func getValueSize() -> [Float] {
        var size: CGSize = CGSize.zero
        guard let value else { return [0,0] }
        AXValueGetValue(value as! AXValue, .cgSize, &size)
        return [Float(size.width), Float(size.height)]
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
        let array = value as! [AnyObject]
        return array.map { UIValue($0) }
    }
    
    public func getValueDictionaryKeys() -> [String] {
        guard let value else { return [] }
        let dictionary = value as! [String: AnyObject]
        return dictionary.keys.map(\.self)
    }
    
    public func getValueDictionaryValue(key: String) -> UIValue? {
        guard let value else { return nil }
        let dictionary = value as! [String: AnyObject]
        return UIValue( dictionary[key]! )
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
        
        guard let elm else {
            return nil
        }
        
        var value: AnyObject?
        let result = AXUIElementCopyAttributeValue(elm, name as CFString, &value)
        
        switch result {
        case .success, .noValue, .notImplemented, .attributeUnsupported:
            guard let value else { return nil }
            return UIValue(value)
        default:
            print("AXUIElementCopyAttributeValue failed: \(name) - \(result)")
            return nil
        }
    }

    func getParent() -> AXUIElement? {
        let parent = getAttributeValue(name: "AXParent") as! AXUIElement?
        return parent
    }
}

