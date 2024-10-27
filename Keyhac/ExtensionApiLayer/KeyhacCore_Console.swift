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

    var writeCallback: ((String) -> Void)?
    var buffer: [String] = []
    
    public func write(s: String) {

        // FIXME: multi threads support

        buffer.append(s)
        
        // limit maximum buffer size
        while buffer.count > 1000 {
            buffer.removeFirst()
        }

        // send buffered strings to the callback
        if let callback = writeCallback {
            callback(buffer.joined())
            buffer = []
        }
    }
}
