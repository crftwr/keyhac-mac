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
            }
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
