//
//  KeyhacApp.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

@main
struct KeyhacApp: App {
    
    init() {
        KeyhacSystem.getInstance().initializePythonSystem()
        KeyhacSystem.getInstance().bootstrapPythonLayer()
        KeyhacSystem.getInstance().installKeyboardHook()
    }
    
    var body: some Scene {
        MenuBarExtra("Keyhac", image: "Keyboard") {
            ContentView()
        }.menuBarExtraStyle(.window)
    }
}
