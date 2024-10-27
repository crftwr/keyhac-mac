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
    
    init() {
        initializePythonSystem()
        bootstrapPythonLayer()
    }
    
    deinit {
        finalizePythonSystem()
    }
    
    func initializePythonSystem() {
        PythonBridge.create(keyhacCoreModuleName, keyhacCoreModuleInit)
    }
    
    func finalizePythonSystem() {
        PythonBridge.destroy()
    }
    
    func initializeKeyboardHook() {
        Hook.getInstance().installKeyboardHook()
    }

    func finalizeKeyboardHook() {
        Hook.getInstance().uninstallKeyboardHook()
    }
    
    func bootstrapPythonLayer(){
        let bundleResourcePath = Bundle.main.resourceURL!.path
        
        let code = """
        import sys
        
        bundle_resource_path = "\(bundleResourcePath)"
        if bundle_resource_path not in sys.path:
            sys.path.insert(0, bundle_resource_path)
        
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
