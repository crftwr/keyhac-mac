//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ConsoleWindowView: View {
    
    @State private var isKeyboardHookEnabled: Bool = KeyhacSystem.getInstance().isKeyboardHookInstalled()
    @State private var errorMessage: String = ""
    
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
                        if !KeyhacSystem.getInstance().checkProcessTrusted() {
                            isKeyboardHookEnabled = false
                            return
                        }
                        
                        KeyhacSystem.getInstance().installKeyboardHook()
                        
                        if KeyhacSystem.getInstance().isKeyboardHookInstalled() {
                            Console.getInstance().write(s: "Installed keyboard hook\n")
                            KeyhacSystem.getInstance().reconfigurePythonLayer()
                        }
                    }
                    else {
                        if KeyhacSystem.getInstance().isKeyboardHookInstalled() {
                            KeyhacSystem.getInstance().uninstallKeyboardHook()
                            Console.getInstance().write(s: "Uninstalled keyboard hook\n")
                        }
                    }
                }
                
                Spacer()
                
                Text(errorMessage)
                    .foregroundColor(.red)
            }
            .padding(.all, 2)
            
            SwiftTermView( viewController: termViewController )
                .lookupKey(termViewKey)
                .frame(minWidth: 100, minHeight: 50, alignment: .center)
        }
        .padding(.all, 10)
    }
}
