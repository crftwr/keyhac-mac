//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct MenuView: View {

    @Environment(\.openWindow) private var openWindow
    @State private var boolTest: Bool = false

    var body: some View {
        
        VStack(alignment: .leading) {
            
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

            Button("About Keyhac"){
                openWindow(id: "about")
                NSApp.activate()
                for window in NSApp.windows {
                    if window.title.contains("About") {
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
        .padding(.all, 10)
    }
}
