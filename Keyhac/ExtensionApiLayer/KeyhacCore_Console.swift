//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-26.
//

import Foundation

public class Console {
    
    private static let instance = Console()
    public static func getInstance() -> Console { return instance }

    private let lock = NSLock()
    
    public enum LogLevel: Int {
        case debug = 10
        case info = 20
        case warning = 30
        case error = 40
        case critical = 50
        case none = 100
    }
    
    var logLevel = LogLevel.info

    var buffer: [String] = []
    var texts: [String: String] = [:]
    
    public func write(msg: String, logLevel: Int = LogLevel.none.rawValue) {
        
        lock.lock()
        defer { lock.unlock() }
        
        if logLevel < self.logLevel.rawValue {
            return
        }
        
        buffer.append(msg)
        
        // limit maximum buffer size
        while buffer.count > 1000 {
            buffer.removeFirst()
        }
    }
    
    public func setText(name: String, text: String) {

        lock.lock()
        defer { lock.unlock() }

        texts[name] = text
    }
    
    public func pullBuffer() -> String {

        lock.lock()
        defer { lock.unlock() }

        let joint_buffer = buffer.joined().replacingOccurrences(of: "\n", with: "\r\n")
        buffer = []
        return joint_buffer
    }
    
    public func setLogLevel(logLevel: LogLevel) {
        self.logLevel = logLevel
    }
    
    public func pullText(name:String) -> String {

        lock.lock()
        defer { lock.unlock() }

        if let text = texts[name] {
            return text
        }
        else {
            return ""
        }
    }
}
