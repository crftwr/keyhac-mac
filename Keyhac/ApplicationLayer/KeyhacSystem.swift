//
//  KeyboardHook.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import Foundation

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
        Hook.getInstance().installKeyboardHook()
    }

    func uninstallKeyboardHook() {
        Hook.getInstance().uninstallKeyboardHook()
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

        if bundle_resource_path not in sys.path:
            sys.path.insert(0, bundle_resource_path)

        #sys.path = [
        #    bundle_resource_path,
        #    os.path.join(bundle_resource_path, "lib/python3.12"),
        #    os.path.join(bundle_resource_path, "lib/python3.12/lib-dynload"),
        #    os.path.join(bundle_resource_path, "lib/python3.12/site-packages"),
        #]
        
        import keyhac_main
        keyhac_main.configure()
        """
        
        if let pythonBridge = PythonBridge.getInstance() {
            pythonBridge.runString(code)
        }
    }

    func reconfigurePythonLayer(){
        let code = """
        import keyhac_main
        keyhac_main.configure()
        """
        
        if let pythonBridge = PythonBridge.getInstance() {
            pythonBridge.runString(code)
        }
    }
}
