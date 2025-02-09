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
    case int
    case float
    case string
    case range
    case point
    case size
    case rect
    case array
    case dictionary
    case unknown
}

public struct ScreenFrame {
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
}

public struct UIValue {
    
    fileprivate var value: AnyObject?
    
    public init() {
    }
    
    public init(_ value: AnyObject) {
        self.value = value
    }
    
    public static func fromBool(_ value: Bool) -> UIValue {
        let cfbool: CFBoolean = value ? kCFBooleanTrue : kCFBooleanFalse
        return .init(cfbool as AnyObject)
    }
    
    public static func fromInt(_ value: Int) -> UIValue {
        let cfnumber: CFNumber = value as CFNumber
        return .init(cfnumber as AnyObject)
    }
    
    public static func fromFloat(_ value: Double) -> UIValue {
        let cfnumber: CFNumber = value as CFNumber
        return .init(cfnumber as AnyObject)
    }
    
    public static func fromString(_ value: String) -> UIValue {
        let cfstr: CFString = value as CFString
        return .init(cfstr as AnyObject)
    }
    
    public static func fromRange(_ value: [Int]) -> UIValue {
        var cfrange: CFRange = CFRange.init(location:value[0], length:value[1])
        let axrange = AXValueCreate(AXValueType.cfRange, &cfrange)
        return .init(axrange as AnyObject)
    }
    
    public static func fromPoint(_ value: [Double]) -> UIValue {
        var cgpoint: CGPoint = CGPoint.init(x:value[0], y:value[1])
        let axpoint = AXValueCreate(AXValueType.cgPoint, &cgpoint)
        return .init(axpoint as AnyObject)
    }
    
    public static func fromSize(_ value: [Double]) -> UIValue {
        var cgsize: CGSize = CGSize.init(width:value[0], height:value[1])
        let axsize = AXValueCreate(AXValueType.cgSize, &cgsize)
        return .init(axsize as AnyObject)
    }
    
    public static func fromRect(_ value: [Double]) -> UIValue {
        var cgrect: CGRect = CGRect.init(x:value[0], y:value[1], width:value[2], height:value[3])
        let axrect = AXValueCreate(AXValueType.cgRect, &cgrect)
        return .init(axrect as AnyObject)
    }
    
    public func getType() -> UIValueType {
        
        guard let value else { return .unknown }
        
        let type = CFGetTypeID(value)
        switch type {
        case CFNumberGetTypeID():
            let cfnumber = value as! CFNumber
            if CFNumberIsFloatType(cfnumber) {
                return .float
            }
            else {
                return .int
            }
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
    
    public func getValueInt() -> Int {
        guard let value else { return 0 }
        return value as! Int
    }
    
    public func getValueFloat() -> Double {
        guard let value else { return 0 }
        return value as! Double
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
    
    public static func getFocusedApplication() -> UIElement? {
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        let pid = NSWorkspace.shared.frontmostApplication?.processIdentifier
        
        guard let pid else {
            return nil
        }
        
        let axapp = AXUIElementCreateApplication(pid)

        return UIElement(axapp as AXUIElement)
    }

    public static func getRunningApplications() -> [UIElement] {
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        var applications: [UIElement] = []
        
        NSWorkspace.shared.runningApplications.forEach {            
            // create AXUIElement from the process id
            let axelement = AXUIElementCreateApplication($0.processIdentifier)
            
            applications.append(UIElement(axelement))
        }

        return applications
    }
    
    public func getAttributeNames() -> [String] {
        
        guard let elm else {
            return []
        }
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

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
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }
        
        var value: AnyObject?
        let result = AXUIElementCopyAttributeValue(elm, name as CFString, &value)
        
        switch result {
        case .success, .noValue, .notImplemented, .attributeUnsupported:
            guard let value else { return nil }
            return UIValue(value)
        default:
            // FIXME: propagate the error to Python layer
            print("AXUIElementCopyAttributeValue failed: \(name) - \(result)")
            return nil
        }
    }
    
    public func setAttributeValue(name: String, value: UIValue) {
        guard let elm else {
            return
        }
        
        guard let value = value.value else {
            return
        }

        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        let result = AXUIElementSetAttributeValue(elm, name as CFString, value)

        switch result {
        case .success:
            break
        default:
            // FIXME: propagate the error to Python layer
            print("AXUIElementSetAttributeValue failed: \(name) - \(result)")
        }
    }

    public func getActionNames() -> [String] {
        
        guard let elm else {
            return []
        }
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        var names: CFArray?
        let result = AXUIElementCopyActionNames(elm, &names)
        if result != .success {
            return []
        }
        
        return names! as [AnyObject] as! [String]
    }
    
    // FIXME: not exposed to Python
    public func getActionDescription(action: String) -> String! {
        
        guard let elm else {
            return nil
        }
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        var description: CFString?
        let result = AXUIElementCopyActionDescription(elm, action as CFString, &description)
        if result != .success {
            return nil
        }
        
        return description as? String
    }
    
    public func performAction(action: String) {
        guard let elm else {
            return
        }
        
        var py_allow_thread = PyAllowThread(true)
        defer { py_allow_thread.End() }

        let result = AXUIElementPerformAction(elm, action as CFString)
        switch result {
        case .success:
            return
        default:
            // FIXME: propagate the error to Python layer
            print("AXUIElementPerformAction failed: \(action) - \(result)")
            return
        }
    }
    
    public static func getScreenFrames() -> [ScreenFrame] {

        var frames: [ScreenFrame] = []
        
        for screen in NSScreen.screens {
            
            print("screen rect", screen.frame)
            
            let frame = ScreenFrame(
                x: screen.frame.origin.x,
                y: screen.frame.origin.y,
                width: screen.frame.size.width,
                height: screen.frame.size.height
            )
            frames.append(frame)
        }
        
        return frames
    }
}

