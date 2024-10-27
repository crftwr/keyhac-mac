//
//  KeyhacCore.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-26.
//

import Foundation

public class Console {
    
    static var writeCallback: ((String) -> Void)?
    
    public static func write(s: String) {
        if let callback = writeCallback {
            callback(s)
        }
    }
}
