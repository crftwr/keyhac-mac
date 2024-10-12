//
//  PythonBridge.hpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

#ifndef PythonBridge_hpp
#define PythonBridge_hpp

#include <stdio.h>
#include <swift/bridging>


class PythonBridge
{
public:
    // static method to handle as reference type
    static PythonBridge * create();
    
    // static method to handle as reference type
    static void destroy(PythonBridge * obj);
    
private:
    // private to handle as reference type
    PythonBridge();
    
    // private to handle as reference type
    PythonBridge(const PythonBridge & src);
    
    // private to handle as reference type
    virtual ~PythonBridge();
    
public:
    int runString(const char * code);
    
} SWIFT_UNSAFE_REFERENCE;

#endif /* PythonBridge_hpp */
