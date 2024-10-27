//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ContentView: View {
    
    @State private var isKeyboardHookEnabled: Bool = false
    
    let termViewKey = UUID().uuidString
    let termViewController = SwiftTermViewController()
    
    var body: some View {
        VStack {
            
            HStack {

                Button("Run ls command"){
                    termViewController.testRunShellCommand(cmd: "ls -al")
                }

                Button("Print Hello"){
                    termViewController.testPrint(line: "Hello World!\r\n")
                }

                Button("Quit"){
                    NSApplication.shared.terminate(nil)
                }

            }
            
            SwiftTermView( viewController: termViewController )
                .lookupKey(termViewKey)
                .frame(width: 400, height: 400, alignment: .center)
                .onAppear() {
                    Console.writeCallback = { s in
                        let s2 = s.replacingOccurrences(of: "\n", with: "\r\n")
                        termViewController.terminal.feed(text: s2)
                    }
                }

            Toggle(isOn: $isKeyboardHookEnabled) {
                Text("Enable keyboard hook")
            }
            .toggleStyle(SwitchToggleStyle(tint: .blue))
            .onChange(of: isKeyboardHookEnabled) { oldValue, newValue in
                if newValue {
                    let result = KeyhacSystem.instance.start()
                    if !result {
                        // keyboard hook instalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = false
                    }
                    KeyhacSystem.instance.configure()
                }
                else {
                    let result = KeyhacSystem.instance.stop()
                    if !result {
                        // keyboard hook uninstalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = true
                    }
                }
            }
        }
        .padding(.all, 10)
    }
}

#Preview {
    ContentView()
}
