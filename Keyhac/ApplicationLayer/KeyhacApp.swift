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
            MenuView()
        }

        Window("Keyhac Console", id: "console") {
            ConsoleWindowView()
        }
        .handlesExternalEvents(matching: ["console"])

        Window("Keyhac Chooser", id: "chooser") {
            ChooserWindowView()
        }
        .windowResizability(.contentSize)
        .handlesExternalEvents(matching: ["chooser"])

        Window("About Keyhac", id: "about") {
            AboutWindowView()
        }
        .windowResizability(.contentSize)
        .handlesExternalEvents(matching: ["about"])
    }
}
