//
//  ContentView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import SwiftUI

struct AboutWindowView: View {
    
    @Environment(\.openURL) private var openURL
    
    var body: some View {
        VStack {
            
            Spacer()
            
            // show icon image
            Image("Logo")
            
            Spacer()
            
            Text("""
                **Keyhac for macOS**
                Version \(appVersion)

                Website: [github/keyhac-mac](https://github.com/crftwr/keyhac-mac)
                Author: [craftware](https://github.com/crftwr)
                
                **3rd party components:**
                Python: \(pythonVersion)
                SwiftTerm: \(swiftTermVersion)
                
                """)
            .textSelection(.enabled)
            
            Spacer()
            
            HStack {
                Button("Copyright notices")
                {
                    let bundleResourcePath = Bundle.main.resourceURL!.path
                    let copyright_notices_path = bundleResourcePath + "/CopyrightNotices"
                    
                    let p = Process()
                    let pipe = Pipe()
                    p.launchPath = "/usr/bin/open"
                    p.arguments = ["-a", "Finder", copyright_notices_path ]
                    p.standardError = pipe
                    p.launch()
                    p.waitUntilExit()
                }
                .buttonStyle(.bordered)
            }
            .padding(.all, 2)
        }
        .frame(width: 250, height: 400)
        .padding(.all, 10)
    }
    
    var appVersion: String {
        if let versionString = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String {
            return versionString
        }
        return "Unknown"
    }
    
    var buildNumber: String {
        if let buildNumberString = Bundle.main.infoDictionary?["CFBundleVersion"] as? String {
            return buildNumberString
        }
        return "Unknown"
    }
    
    var pythonVersion: String {
        let versionString = PythonBridge.getVersion()
        return String(versionString)
    }
    
    var swiftTermVersion: String {
        return "1.2.1"
    }
}
