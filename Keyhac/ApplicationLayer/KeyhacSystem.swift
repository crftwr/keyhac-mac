//
//  KeyboardHook.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import Foundation
import ApplicationServices

class KeyhacSystem {
    
    private static let instance = KeyhacSystem()
    static func getInstance() -> KeyhacSystem { return instance }

    func initializePythonSystem() {
        PythonBridge.create(keyhacCoreModuleName, keyhacCoreModuleInit)
    }
    
    func finalizePythonSystem() {
        PythonBridge.destroy()
    }
    
    func installKeyboardHook() {
        if checkProcessTrusted() {
            Hook.getInstance().installKeyboardHook()
        }
    }

    func uninstallKeyboardHook() {
        Hook.getInstance().uninstallKeyboardHook()
    }
    
    func checkProcessTrusted() -> Bool {
        let options: NSDictionary = [kAXTrustedCheckOptionPrompt.takeRetainedValue() as NSString: true]
        return AXIsProcessTrustedWithOptions(options)
    }
    
    func isKeyboardHookInstalled() -> Bool {
        return Hook.getInstance().isKeyboardHookInstalled()
    }
    
    func bootstrapPythonLayer(){
        let bundleResourcePath = Bundle.main.resourceURL!.path
        
        let code = """
        import sys
        import os
        
        bundle_resource_path = "\(bundleResourcePath)"

        sys.path = [
            bundle_resource_path,
            os.path.join(bundle_resource_path, "PythonLibs/python3.12"),
            os.path.join(bundle_resource_path, "PythonLibs/python3.12/lib-dynload"),
            os.path.join(os.path.expanduser("~/.keyhac/extensions")),
        ]
        
        import keyhac_main
        keyhac_main.configure()
        """
        
        if let pythonBridge = PythonBridge.getInstance() {

            var gil = PyGIL(true);
            defer { gil.Release() }

            pythonBridge.runString(code)
        }
    }

    func reconfigurePythonLayer(){
        let code = """
        import keyhac_main
        keyhac_main.configure()
        """
        
        if let pythonBridge = PythonBridge.getInstance() {

            var gil = PyGIL(true);
            defer { gil.Release() }

            pythonBridge.runString(code)
        }
    }
}
