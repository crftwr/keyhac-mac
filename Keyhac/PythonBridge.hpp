//
//  PythonBridge.hpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

#ifndef PythonBridge_hpp
#define PythonBridge_hpp

#include <stdio.h>

class PythonBridge
{
public:
    static PythonBridge * getInstance();
    
    PythonBridge();
    virtual ~PythonBridge();
    
    int callFunction();
    
private:
    static PythonBridge * instance;
};

#endif /* PythonBridge_hpp */
