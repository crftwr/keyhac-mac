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
    
    var body: some View {
        VStack {
            
            HStack {

                Button("Run ls command"){

                    let view = SwiftTermView.lookup(termViewKey)
                    if let view = view {
                        if let term = view as? SwiftTermView {
                            term.viewController.testRunShellCommand(cmd: "ls -al")
                        }
                    }
                }

                Button("Print Hello"){

                    let view = SwiftTermView.lookup(termViewKey)
                    if let view = view {
                        if let term = view as? SwiftTermView {
                            term.viewController.testPrint(line: "Hello World!\r\n")
                        }
                    }
                }

                Button("Quit"){
                    NSApplication.shared.terminate(nil)
                }

            }
            
            SwiftTermView( viewController: SwiftTermViewController() )
                .lookupKey(termViewKey)
                .frame(width: 400, height: 400, alignment: .center)
                /*
                .onAppear() {
                    Console.writeCallback = { s in
                        let view = SwiftTermView.lookup(termViewKey)
                        if let view = view {
                            if let term = view as? SwiftTermView {
                                term.viewController.terminal.feed(text: s)
                            }
                        }
                    }
                }
                */

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
