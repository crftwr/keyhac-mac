//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ConsoleWindowView: View {
    
    @State private var isKeyboardHookEnabled: Bool = KeyhacSystem.getInstance().isKeyboardHookInstalled()
    
    let logLevels = ["Debug", "Info", "Warning", "Error", "Critical"]
    @State var logLevel = "Info"
    
    let termViewKey = UUID().uuidString
    let termViewController = SwiftTermViewController()

    @State var lastKeyString: String = ""
    @State var focusPathString: String = ""

    var body: some View {
        VStack {
            
            HStack {

                Toggle(isOn: $isKeyboardHookEnabled ) {
                    Image("Keyboard")
                        .renderingMode(.template)
                        .foregroundColor(.black)
                        .imageScale(.large)
                }
                .toggleStyle(SwitchToggleStyle(tint: .blue))
                .frame(minWidth: 100)
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
                
                Picker("Log level:", selection: $logLevel) {
                    ForEach(logLevels, id: \.self) {
                        Text($0)
                    }
                }
                .pickerStyle(.menu)
                .frame(width: 150)
            }
            
            SwiftTermView( viewController: termViewController )
                .lookupKey(termViewKey)
                .frame(minWidth: 100, minHeight: 50, alignment: .center)
            
            Grid {
                GridRow {
                    Text("Last key:")
                        .gridColumnAlignment(.trailing)
                    Text(lastKeyString)
                        .padding(.all, 2)
                        .frame(maxWidth: .infinity)
                        .overlay(
                            RoundedRectangle(cornerRadius: 4)
                                .stroke(.gray, lineWidth: 1)
                            )
                        .textSelection(.enabled)

                    Button("Copy") {
                        print("Copied")
                    }
                }
                
                GridRow {
                    Text("Focus path:")
                    Text(focusPathString)
                        .padding(.all, 2)
                        .frame(maxWidth: .infinity)
                        .overlay(
                            RoundedRectangle(cornerRadius: 4)
                                .stroke(.gray, lineWidth: 1)
                            )
                        .textSelection(.enabled)

                    Button("Copy") {
                        print("Copied")
                    }
                }
            }
            .padding(.all, 4)
        }
        .padding(.all, 10)
    }
}
