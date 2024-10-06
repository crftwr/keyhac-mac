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
                print("isKeyboardHookEnabled changed to \(newValue)")
                if newValue {
                    let result = KeyboardHook.instance.install()
                    if !result {
                        // keyboard hook instalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = false
                    }
                }
                else {
                    let result = KeyboardHook.instance.uninstall()
                    if !result {
                        // keyboard hook uninstalaltion failed, so reverting toggle status
                        isKeyboardHookEnabled = true
                    }
                }
            }
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
