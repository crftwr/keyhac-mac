//
//  PythonBridge.hpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

#ifndef PythonBridge_hpp
#define PythonBridge_hpp

#include <stdio.h>


class KeyboardHookCpp
{
    typedef int (*callback_t)(void*,int);

public:
    KeyboardHookCpp(
        void * swift_obj,
        callback_t callbackTest1
    );
    ~KeyboardHookCpp();
    
    void * swift_obj;
    callback_t callbackTest1;
    
    int test1(int i);
};


class PythonBridge
{
public:
    static PythonBridge * getInstance();
    
    PythonBridge();
    virtual ~PythonBridge();
    
    int runString(const char * code);
    
private:
    static PythonBridge * instance;
};

#endif /* PythonBridge_hpp */
