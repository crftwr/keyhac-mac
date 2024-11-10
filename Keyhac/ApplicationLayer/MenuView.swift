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
            .keyboardShortcut("o")

            Divider()

            Button("Edit config.py"){

                let config_file_path = NSString(string: "~/.keyhac/config.py").expandingTildeInPath
                let editors = ["Visual Studio Code", "Xcode", "TextEdit"]
                var resultCode:Int32 = 0
                var errorMessage: String = ""
                
                for editor in editors {
                    let p = Process()
                    let pipe = Pipe()
                    p.launchPath = "/usr/bin/open"
                    p.arguments = ["-a", editor, config_file_path ]
                    p.standardError = pipe
                    p.launch()
                    p.waitUntilExit()
                    resultCode = p.terminationStatus
                    if resultCode == 0 {
                        break
                    }
                    else {
                        let errorMessageData = pipe.fileHandleForReading.readDataToEndOfFile()
                        errorMessage = String(data: errorMessageData, encoding: .utf8)!
                    }
                }
                
                if resultCode == 0 {
                    Console.getInstance().write(s: "Opened config.py\n")
                }
                else {
                    Console.getInstance().write(s: "Error: ")
                    Console.getInstance().write(s: errorMessage)
                }
            }
            .keyboardShortcut("e")

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
            .keyboardShortcut("a")

            Divider()

            Button("Quit Keyhac"){
                NSApplication.shared.terminate(nil)
            }.keyboardShortcut("q")
        }
        .padding(.all, 10)
    }
}
