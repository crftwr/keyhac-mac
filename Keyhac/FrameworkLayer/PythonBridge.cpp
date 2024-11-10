//
//  PythonBridge.cpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-06.
//

#include <stdio.h>
#include "Python.h"
#include "PythonBridge.hpp"

#include "Keyhac-Swift.h"


// ------------------------------------------

PyObjectPtr::PyObjectPtr()
    :
    p(NULL)
{
}

PyObjectPtr::PyObjectPtr(PyObject * _p)
    :
    p(_p)
{
}

void PyObjectPtr::IncRef()
{
    Py_XINCREF(p);
}

void PyObjectPtr::DecRef()
{
    Py_XDECREF(p);
}


// ------------------------------------------

PyAllowThread::PyAllowThread(bool begin)
    :
    state(NULL)
{
    if(begin)
    {
        Begin();
    }
}

PyAllowThread::~PyAllowThread()
{
    End();
}
    
void PyAllowThread::Begin()
{
    if(!state)
    {
        state = PyEval_SaveThread();
    }
}

void PyAllowThread::End()
{
    if(state)
    {
        PyEval_RestoreThread(state);
        state = NULL;
    }
}


// ------------------------------------------

PyGIL::PyGIL(bool acquire)
    :
    acquired(false),
    state(0)
{
    if(acquire)
    {
        Acquire();
    }
}

PyGIL::~PyGIL()
{
    Release();
}
    
void PyGIL::Acquire()
{
    if(!acquired)
    {
        state = PyGILState_Ensure();
        acquired = true;
    }
}

void PyGIL::Release()
{
    if(acquired)
    {
        PyGILState_Release((PyGILState_STATE)state);
        acquired = false;
    }
}


// ------------------------------------------

PythonBridge * PythonBridge::instance;

void PythonBridge::create( const char * module_name, PythonModuleInitFunc module_init_func)
{
    instance = new PythonBridge(module_name, module_init_func);
}

PythonBridge * PythonBridge::getInstance()
{
    return instance;
}

void PythonBridge::destroy()
{
    delete instance;
    instance = NULL;
}

PythonBridge::PythonBridge(const char * module_name, PythonModuleInitFunc module_init_func)
{
    if (PyImport_AppendInittab(module_name, module_init_func) == -1)
    {
        printf("Error: could not extend in-built modules table\n");
        exit(1);
    }
    
    PyConfig config;
    PyConfig_InitPythonConfig(&config);
    config.isolated = 1;
    config.use_environment = 0;
    config.user_site_directory = 0;
    
    Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);

    py_thread_state = PyEval_SaveThread();
}
    
PythonBridge::~PythonBridge()
{
    PyEval_RestoreThread((PyThreadState*)py_thread_state);
    
    Py_Finalize();
}

int PythonBridge::runString(const char * code)
{
    return PyRun_SimpleString(code);
}

PyObjectPtr PythonBridge::invokeCallable(const PyObjectPtr & callable, const PyObjectPtr & arg)
{
    PyObject * pyarglist = Py_BuildValue("(O)", arg.ptr());
    PyObject * pyresult = PyObject_Call( callable.ptr(), pyarglist, NULL );
    Py_DECREF(pyarglist);
    
    if(!pyresult)
    {
        PyErr_Print();
    }
    
    return pyresult;
}

PyObjectPtr PythonBridge::buildPythonString(const char * s)
{
    PyObject * pyobj = Py_BuildValue("s",s);
    return pyobj;
}

int PythonBridge::parsePythonInt(const PyObjectPtr & obj)
{
    int i;
    if( obj.ptr()==Py_None )
    {
        i = 0;
    }
    else
    {
        PyArg_Parse(obj.ptr(),"i", &i );
    }
    return i;
}

std::string PythonBridge::getVersion()
{
    char buf[64];
    snprintf(buf, sizeof(buf), "%d.%d.%d", PY_MAJOR_VERSION, PY_MINOR_VERSION, PY_MICRO_VERSION);
    return std::string(buf);
}
