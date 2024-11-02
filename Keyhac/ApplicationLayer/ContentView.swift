//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct ContentView: View {
    
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
                        checkProcessTrusted()
                        
                        KeyhacSystem.getInstance().installKeyboardHook()
                        Console.getInstance().write(s: "Installed keyboard hook\n")

                        KeyhacSystem.getInstance().reconfigurePythonLayer()
                    }
                    else {
                        KeyhacSystem.getInstance().uninstallKeyboardHook()
                        Console.getInstance().write(s: "Uninstalled keyboard hook\n")
                    }
                }
                
                Spacer()
                
                Text(errorMessage)
                    .foregroundColor(.red)
            }
            .padding(.all, 2)
            
            SwiftTermView( viewController: termViewController )
                .lookupKey(termViewKey)
                .frame(width: 400, height: 400, alignment: .center)

            HStack {
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

                Button("Quit"){
                    NSApplication.shared.terminate(nil)
                }
            }
        }
        .padding(.all, 10)
    }
    
    func checkProcessTrusted() {
        let options : NSDictionary = [kAXTrustedCheckOptionPrompt.takeRetainedValue() as NSString: true]
        let isTrusted = AXIsProcessTrustedWithOptions(options)
        
        if isTrusted {
            errorMessage = ""
        }
        else {
            errorMessage = "Accessibility is not enabled."
        }
    }
}

#Preview {
    ContentView()
}
