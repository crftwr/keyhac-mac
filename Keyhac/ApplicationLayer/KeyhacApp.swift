//
//  KeyhacApp.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

@main
struct KeyhacApp: App {
    var body: some Scene {        
        MenuBarExtra("Keyhac", systemImage: "hammer") {
            ContentView()
        }.menuBarExtraStyle(.window)
    }
}
