//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ContentView: View {
    
    @State private var isKeyboardHookEnabled: Bool = false
    
    var body: some View {
        VStack {
            Toggle(isOn: $isKeyboardHookEnabled) {
                Text("Enable keyboard hook")
            }
            .toggleStyle(SwitchToggleStyle(tint: .blue))
            .onChange(of: isKeyboardHookEnabled) { oldValue, newValue in
                if newValue {
                    // Install keyboard hook to the OS
                    let result = KeyboardHook.instance.install()
                    if !result {
                        // keyboard hook instalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = false
                    }
                    
                    // configure keyboard hook behavior
                    KeyboardHook.instance.configure()
                }
                else {
                    // Uninstall the keyboard hook
                    let result = KeyboardHook.instance.uninstall()
                    if !result {
                        // keyboard hook uninstalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = true
                    }
                }
            }
            
            Divider()
            
            Button("Test"){
                KeyboardHook.instance.callbackTest()
            }

            Divider()
            
            Button("Quit"){
                NSApplication.shared.terminate(nil)
            }
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
