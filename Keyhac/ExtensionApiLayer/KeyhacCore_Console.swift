//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-26.
//

import Foundation

protocol ConsoleVisualizeDelegate {
    func write(s: String)
    func setText(name: String, text: String)
}

public class Console {
    
    private static let instance = Console()
    public static func getInstance() -> Console { return instance }
    
    var delegate: ConsoleVisualizeDelegate? = nil

    var buffer: [String] = []
    
    public func write(s: String) {

        // FIXME: multi threads support

        buffer.append(s)
        
        // limit maximum buffer size
        while buffer.count > 1000 {
            buffer.removeFirst()
        }

        // send buffered strings to the callback
        if let delegate = delegate {
            delegate.write(s: buffer.joined())
            buffer = []
        }
    }
    
    public func setText(name: String, text: String) {
        if let delegate = delegate {
            delegate.setText(name: name, text: text)
        }
    }
}
