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
            
            Divider()
            
            Button("Test"){
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
