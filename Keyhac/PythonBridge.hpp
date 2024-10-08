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


class KeyboardHookCpp
{
public:
    typedef int (*callback_t)(void*,int);

    // static method to handle as reference type
    static KeyboardHookCpp * create(
        void * swift_obj,
        callback_t callbackTest1
        );
    
    // static method to handle as reference type
    static void destroy(KeyboardHookCpp * obj);
    
private:
    // private to handle as reference type
    KeyboardHookCpp(
        void * swift_obj,
        callback_t callbackTest1
    );
    
    // private to handle as reference type
    KeyboardHookCpp(const KeyboardHookCpp & src);
    
    // private to handle as reference type
    virtual ~KeyboardHookCpp();
    
public:
    int test1(int i);

private:
    void * swift_obj;
    callback_t callbackTest1;
    
} SWIFT_UNSAFE_REFERENCE;


class PythonBridge
{
public:
    static PythonBridge & getInstance();
    
    PythonBridge();
    virtual ~PythonBridge();
    
    int runString(const char * code);
    
private:
    static PythonBridge * instance;
};

#endif /* PythonBridge_hpp */
