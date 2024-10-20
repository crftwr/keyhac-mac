//
//  KeyhacCore.cpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-18.
//

#include <stdio.h>
#include "Python.h"
#include "PythonBridge.hpp"
#include "KeyhacCore.hpp"

#include "Keyhac-Swift.h"

#define MODULE_NAME "keyhac_core"


const char * keyhacCoreModuleName = MODULE_NAME;

// ------------------------------------------

struct Hook_Object
{
    PyObject_HEAD
    Keyhac::Hook impl;
};

static int Hook_init(Hook_Object * self, PyObject * args, PyObject * kwds)
{
    if( ! PyArg_ParseTuple( args, "" ) )
    {
        return -1;
    }
    
    self->impl = Keyhac::Hook::init();

    return 0;
}

static void Hook_dealloc(Hook_Object * self)
{
    self->impl.~Hook();

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject * Hook_getattr(Hook_Object * self, PyObject * pyattrname)
{
    return PyObject_GenericGetAttr((PyObject*)self, pyattrname);
}

static int Hook_setattr(Hook_Object * self, PyObject * pyattrname, PyObject * pyvalue)
{
    return PyObject_GenericSetAttr((PyObject*)self, pyattrname,pyvalue);
}

static PyObject * Hook_destroy(Hook_Object * self, PyObject* args)
{
    if( ! PyArg_ParseTuple(args, "" ) )
    {
        return NULL;
    }
    
    self->impl.destroy();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Hook_setCallback(Hook_Object * self, PyObject* args)
{
    PyObject * pyname;
    PyObject * pycallback;
    if( ! PyArg_ParseTuple(args, "UO", &pyname, &pycallback ) )
    {
        return NULL;
    }
    
    const char * name = PyUnicode_AsUTF8AndSize(pyname, NULL);
    printf("Hook_setCallback - %s\n", name);
    
    if(pycallback!=Py_None)
    {
        auto callback = swift::Optional<PyObjectPtr>::some(PyObjectPtr(pycallback));
        self->impl.setCallback(name, callback);
    }
    else
    {
        auto callback = swift::Optional<PyObjectPtr>::none();
        self->impl.setCallback(name, callback);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Hook_sendKeyboardEvent(Hook_Object * self, PyObject* args)
{
    PyObject * pytype;
    int keyCode;
    if( ! PyArg_ParseTuple(args, "UI", &pytype, &keyCode ) )
    {
        return NULL;
    }
    
    const char * type = PyUnicode_AsUTF8AndSize(pytype, NULL);
    
    self->impl.sendKeyboardEvent(type, keyCode);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Hook_methods[] = {
    { "destroy", (PyCFunction)Hook_destroy, METH_VARARGS, "" },
    { "setCallback", (PyCFunction)Hook_setCallback, METH_VARARGS, "" },
    { "sendKeyboardEvent", (PyCFunction)Hook_sendKeyboardEvent, METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Hook_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Hook",                 /* tp_name */
    sizeof(Hook_Type),      /* tp_basicsize */
    0,                      /* tp_itemsize */
    (destructor)Hook_dealloc,/* tp_dealloc */
    0,                      /* tp_print */
    0,                      /* tp_getattr */
    0,                      /* tp_setattr */
    0,                      /* tp_compare */
    0,                      /* tp_repr */
    0,                      /* tp_as_number */
    0,                      /* tp_as_sequence */
    0,                      /* tp_as_mapping */
    0,                      /* tp_hash */
    0,                      /* tp_call */
    0,                      /* tp_str */
    (getattrofunc)Hook_getattr, /* tp_getattro */
    (setattrofunc)Hook_setattr, /* tp_setattro */
    0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "",                     /* tp_doc */
    0,                      /* tp_traverse */
    0,                      /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    Hook_methods,           /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    (initproc)Hook_init,    /* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

static PyObject * _getFocus(PyObject *self, PyObject *args)
{
    std::string focus = Keyhac::Gui::getFocus();
    
    //return PyLong_FromLong(0);
    return PyUnicode_FromString(focus.c_str());
}

static PyMethodDef keyhac_core_methods[] = {
    {"getFocus", _getFocus, METH_VARARGS, "Get focus information in string format"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef keyhac_core_module = {
    PyModuleDef_HEAD_INIT,
    MODULE_NAME,   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    keyhac_core_methods
};

PyObject * keyhacCoreModuleInit(void)
{
    if( PyType_Ready(&Hook_Type)<0 ) return NULL;
    
    PyObject *m, *d;

    m = PyModule_Create(&keyhac_core_module);
    if(m == NULL) return NULL;

    Py_INCREF(&Hook_Type);
    PyModule_AddObject( m, "Hook", (PyObject*)&Hook_Type );

    d = PyModule_GetDict(m);

    /*
    g->Error = PyErr_NewException( MODULE_NAME".Error", NULL, NULL);
    PyDict_SetItemString( d, "Error", g->Error );
    */

    if( PyErr_Occurred() )
    {
        Py_FatalError( "can't initialize module " MODULE_NAME );
    }

    return m;
}
