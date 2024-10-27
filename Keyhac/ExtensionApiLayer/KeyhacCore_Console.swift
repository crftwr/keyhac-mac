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
    
    public func write(s: String) {
        if let callback = writeCallback {
            callback(s)
        }
    }
}
