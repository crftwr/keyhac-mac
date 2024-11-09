//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct MenuView: View {

    @Environment(\.openWindow) private var openWindow

    var body: some View {

        Button("Open Console"){
            openWindow(id: "console")
            NSApp.activate()
            for window in NSApp.windows {
                if window.title.contains("Console") {
                    window.makeKeyAndOrderFront(nil)
                    break
                }
            }
        }

        Divider()
        
        Button("Quit Keyhac"){
            NSApplication.shared.terminate(nil)
        }.keyboardShortcut("q")
    }
}
