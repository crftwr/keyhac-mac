//
//  ViewLookup.swift
//  SwiftTermEmbed
//
//  Created by Tomonori Shimomura on 2024-10-26.
//

import SwiftUI

var lookupTable: [String: any View] = [:]

extension View {
    func lookupKey(_ key: String) -> Self {
        lookupTable[key] = self
        return self
    }
    
    static func lookup(_ key: String) -> (any View)? {
        return lookupTable[key]
    }
}
