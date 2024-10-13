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

extern "C" {
    struct _object;
    typedef struct _object PyObject;
}

class PyObjectPtr
{
public:
    PyObjectPtr();
    PyObjectPtr(PyObject * p);
    
    void IncRef();
    void DecRef();

    PyObject * ptr() const {return p;}

private:
    PyObject * p;
};



class PythonBridge
{
public:
    // static method to handle as reference type
    static void create();
    
    static PythonBridge * getInstance();
    
    // static method to handle as reference type
    static void destroy();
    
private:
    // private to handle as reference type
    PythonBridge();
    
    // private to handle as reference type
    PythonBridge(const PythonBridge & src);
    
    // private to handle as reference type
    virtual ~PythonBridge();

    static PythonBridge * instance;
    
public:
    int runString(const char * code);
    int invokeCallable(const PyObjectPtr & callable, const PyObjectPtr & arg);
    
    // FIXME: なぜか static method にしないと動かない
    static PyObjectPtr buildPythonString(const char * s);

} SWIFT_UNSAFE_REFERENCE;

#endif /* PythonBridge_hpp */
