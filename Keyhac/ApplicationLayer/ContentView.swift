//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ContentView: View {
    
    @State private var isKeyboardHookEnabled: Bool = KeyhacSystem.getInstance().isKeyboardHookInstalled()
    
    let termViewKey = UUID().uuidString
    let termViewController = SwiftTermViewController()

    var body: some View {
        VStack {
            
            HStack {
                Toggle(isOn: $isKeyboardHookEnabled ) {
                    Text("Keyboard Hook")
                }
                .toggleStyle(SwitchToggleStyle(tint: .blue))
                .onChange(of: isKeyboardHookEnabled) { oldValue, newValue in
                    if newValue {
                        KeyhacSystem.getInstance().installKeyboardHook()
                        Console.getInstance().write(s: "Installed keyboard hook\n")

                        KeyhacSystem.getInstance().reconfigurePythonLayer()
                    }
                    else {
                        KeyhacSystem.getInstance().uninstallKeyboardHook()
                        Console.getInstance().write(s: "Uninstalled keyboard hook\n")
                    }
                }
            }
            
            SwiftTermView( viewController: termViewController )
                .lookupKey(termViewKey)
                .frame(width: 400, height: 400, alignment: .center)

            HStack {
                Button("Edit config.py"){
                }

                Button("Quit"){
                    NSApplication.shared.terminate(nil)
                }
            }
        }
        .padding(.all, 10)
    }
}

#Preview {
    ContentView()
}
