//
//  PythonBridge.cpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

#include <stdio.h>
#include "Python.h"
#include "PythonBridge.hpp"


// ------------------------------------------

KeyboardHookCpp * KeyboardHookCpp::create(
    void * _swift_obj,
    callback_t _callbackTest1
    )
{
    return new KeyboardHookCpp(_swift_obj, _callbackTest1);
}

void KeyboardHookCpp::destroy(KeyboardHookCpp * obj)
{
    delete obj;
}

KeyboardHookCpp::KeyboardHookCpp(
    void * _swift_obj,
    callback_t _callbackTest1
    )
    :
    swift_obj(_swift_obj),
    callbackTest1(_callbackTest1)
{
    printf("KeyboardHookCpp::KeyboardHookCpp()\n");
}

KeyboardHookCpp::~KeyboardHookCpp()
{
    printf("KeyboardHookCpp::~KeyboardHookCpp()\n");
}

int KeyboardHookCpp::test1(int i)
{
    printf("KeyboardHookCpp::test1()\n");

    if(callbackTest1)
    {
        return (*callbackTest1)(swift_obj,i);
    }
    else
    {
        return 0;
    }
}

// ------------------------------------------

static PyObject * keyhac_core_test1(PyObject *self, PyObject *args)
{
    printf("keyhac_core_test1 was called\n");
    return PyLong_FromLong(0);
}

static PyMethodDef keyhac_core_methods[] = {
    {"test1", keyhac_core_test1, METH_VARARGS, "Test function"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef keyhac_core_module = {
    PyModuleDef_HEAD_INIT,
    "keyhac_core",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    keyhac_core_methods
};

PyMODINIT_FUNC
PyInit_keyhac_core(void)
{
    PyObject *m;

    m = PyModule_Create(&keyhac_core_module);
    if (m == NULL)
        return NULL;

    return m;
}


// ------------------------------------------

PythonBridge * PythonBridge::instance;

PythonBridge & PythonBridge::getInstance()
{
    if(!instance)
    {
        instance = new PythonBridge();
    }
    return (*instance);
}

PythonBridge::PythonBridge()
{
    printf("PythonBridge::PythonBridge\n");
    
    if (PyImport_AppendInittab("keyhac_core", PyInit_keyhac_core) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }
    
    Py_Initialize();
}
    
PythonBridge::~PythonBridge()
{
    printf("PythonBridge::~PythonBridge\n");
}

int PythonBridge::runString(const char * code)
{
    return PyRun_SimpleString(code);
}
