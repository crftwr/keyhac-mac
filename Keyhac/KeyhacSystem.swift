//
//  KeyboardHook.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

import Foundation

class KeyhacSystem {
    
    static let instance = KeyhacSystem()
    
    func start() -> Bool {
        
        if PythonBridge.getInstance() != nil {
            print("KeyhacSystem is already running.")
            return true;
        }
        
        initializePython()

        return true
    }
    
    func stop() -> Bool {

        if PythonBridge.getInstance() == nil {
            print("KeyhacSystem is not running.")
            return true;
        }
        
        terminatePython()

        return true
    }

    func initializePython() {
        PythonBridge.create(keyhacCoreModuleName, keyhacCoreModuleInit)
    }
    
    func terminatePython() {
        PythonBridge.destroy()
    }
    
    func configure(){
        
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
}
