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

using namespace Keyhac;

const char * keyhacCoreModuleName = MODULE_NAME;


// ------------------------------------------

extern PyTypeObject UIElement_Type;

struct UIElement_Object
{
    PyObject_HEAD
    UIElement impl;
};

static UIElement_Object * _createPyUIElement(const UIElement & uiElement)
{
    UIElement_Object * pyUIElement = (UIElement_Object*)UIElement_Type.tp_alloc(&UIElement_Type, 0);
    pyUIElement->impl = uiElement;
    
    return pyUIElement;
}

static PyObject * _convertUIValueToPyObject(const UIValue & value)
{
    PyObject * pyvalue = NULL;
    
    auto type = value.getType();
    switch (type) {
        case UIValueType::cases::bool_:
            {
                bool b = value.getValueBool();
                if(b)
                {
                    pyvalue = Py_True;
                }
                else
                {
                    pyvalue = Py_False;
                }
                Py_INCREF(pyvalue);
            }
            break;
                
        case UIValueType::cases::number:
            {
                long i = value.getValueNumber();
                pyvalue = PyLong_FromLong(i);
            }
                break;
                
        case UIValueType::cases::string:
            {
                std::string s = value.getValueString();
                pyvalue = PyUnicode_DecodeUTF8( s.c_str(), s.length(), "replace");
            }
            break;

        case UIValueType::cases::range:
            {
                auto range = value.getValueRange();
                pyvalue = Py_BuildValue( "(ii)", range[0], range[1] );
            }
            break;
                
        case UIValueType::cases::point:
            {
                auto rect = value.getValueRect();
                pyvalue = Py_BuildValue( "(ff)", rect[0], rect[1] );
            }
            break;
                
        case UIValueType::cases::size:
            {
                auto rect = value.getValueRect();
                pyvalue = Py_BuildValue( "(ff)", rect[0], rect[1] );
            }
            break;
                
        case UIValueType::cases::rect:
            {
                auto rect = value.getValueRect();
                pyvalue = Py_BuildValue( "(ffff)", rect[0], rect[1], rect[2], rect[3] );
            }
            break;
                
        case UIValueType::cases::uiElement:
            {
                UIElement uiElement = value.getValueUIElement();
                pyvalue = (PyObject*)_createPyUIElement(uiElement);
            }
            break;
                
        case UIValueType::cases::array:
            {
                auto array = value.getValueArray();
                
                PyObject * pylist = PyList_New(0);
                
                for( swift::Int i=array.getStartIndex() ; i<array.getEndIndex() ; ++i )
                {
                    UIValue item = array[i];
                    
                    PyObject * pyitem = _convertUIValueToPyObject(item);
                    PyList_Append( pylist, pyitem );
                    Py_XDECREF(pyitem);
                }
                
                pyvalue = pylist;
            }
            break;

        case UIValueType::cases::dictionary:
            {
                auto keys = value.getValueDictionaryKeys();
                
                PyObject * pydict = PyDict_New();
                
                // iterate keys
                for( swift::Int i=keys.getStartIndex() ; i<keys.getEndIndex() ; ++i )
                {
                    std::string dict_key = keys[i];
                    auto dict_value = value.getValueDictionaryValue(dict_key.c_str());
                    
                    PyObject * pykey = PyUnicode_DecodeUTF8( dict_key.c_str(), dict_key.length(), "replace");
                    PyObject * pyvalue = _convertUIValueToPyObject(dict_value.get());

                    PyDict_SetItem(pydict, pykey, pyvalue);
                    
                    Py_XDECREF(pykey);
                    Py_XDECREF(pyvalue);
                }
                
                pyvalue = pydict;
            }
            break;

        default:
            break;
    }
    
    if(pyvalue)
    {
        return pyvalue;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static int UIElement_init(UIElement_Object * self, PyObject * args, PyObject * kwds)
{
    if( ! PyArg_ParseTuple( args, "" ) )
    {
        return -1;
    }
    
    self->impl = UIElement::init();

    return 0;
}

static void UIElement_dealloc(UIElement_Object * self)
{
    self->impl.~UIElement();

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject * UIElement_getattr(UIElement_Object * self, PyObject * pyattrname)
{
    return PyObject_GenericGetAttr((PyObject*)self, pyattrname);
}

static int UIElement_setattr(UIElement_Object * self, PyObject * pyattrname, PyObject * pyvalue)
{
    return PyObject_GenericSetAttr((PyObject*)self, pyattrname,pyvalue);
}

static UIElement_Object * UIElement_getSystemWideElement( PyObject * self, PyObject * args )
{
    if( ! PyArg_ParseTuple(args,"") )
        return NULL;
    
    UIElement elm = UIElement::getSystemWideElement();
    UIElement_Object * pyelm = _createPyUIElement(elm);
    
    return pyelm;
}

static PyObject * UIElement_getAttributeNames(UIElement_Object * self, PyObject * args)
{
    if( ! PyArg_ParseTuple(args,"") )
        return NULL;
    
    PyObject * pyattr_names = PyList_New(0);

    auto attr_names = self->impl.getAttributeNames();
    for( swift::Int i=attr_names.getStartIndex() ; i<attr_names.getEndIndex() ; ++i )
    {
        std::string attr_name = attr_names[i];

        PyObject * pyitem = Py_BuildValue( "s", attr_name.c_str() );
        PyList_Append( pyattr_names, pyitem );
        Py_XDECREF(pyitem);
    }
    
    return pyattr_names;
}

static PyObject * UIElement_getAttributeValue(UIElement_Object * self, PyObject * args)
{
    PyObject * pyattr_name;
    if( ! PyArg_ParseTuple(args, "U", &pyattr_name ) )
    {
        return NULL;
    }
    
    const char * attr_name = PyUnicode_AsUTF8AndSize(pyattr_name, NULL);
    
    PyObject * pyvalue = NULL;

    auto wrapped_value = self->impl.getAttributeValue(attr_name);
    if(wrapped_value)
    {
        UIValue value = wrapped_value.get();
        pyvalue = _convertUIValueToPyObject(value);
    }
    
    if(pyvalue)
    {
        return pyvalue;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static PyObject * UIElement_getActionNames(UIElement_Object * self, PyObject * args)
{
    if( ! PyArg_ParseTuple(args,"") )
        return NULL;
    
    PyObject * pyaction_names = PyList_New(0);

    auto action_names = self->impl.getActionNames();
    for( swift::Int i=action_names.getStartIndex() ; i<action_names.getEndIndex() ; ++i )
    {
        std::string action_name = action_names[i];

        PyObject * pyitem = Py_BuildValue( "s", action_name.c_str() );
        PyList_Append( pyaction_names, pyitem );
        Py_XDECREF(pyitem);
    }
    
    return pyaction_names;
}

static PyObject * UIElement_performAction(UIElement_Object * self, PyObject * args)
{
    PyObject * pyaction;
    if( ! PyArg_ParseTuple(args, "U", &pyaction ) )
    {
        return NULL;
    }
    
    const char * action = PyUnicode_AsUTF8AndSize(pyaction, NULL);
    
    self->impl.performAction(action);
    
    // FIXME: handle error

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef UIElement_methods[] = {
    { "getSystemWideElement", (PyCFunction)UIElement_getSystemWideElement, METH_STATIC|METH_VARARGS, "" },
    { "getAttributeNames", (PyCFunction)UIElement_getAttributeNames, METH_VARARGS, "" },
    { "getAttributeValue", (PyCFunction)UIElement_getAttributeValue, METH_VARARGS, "" },
    { "getActionNames", (PyCFunction)UIElement_getActionNames, METH_VARARGS, "" },
    { "performAction", (PyCFunction)UIElement_performAction, METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject UIElement_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "UIElement",            /* tp_name */
    sizeof(UIElement_Type), /* tp_basicsize */
    0,                      /* tp_itemsize */
    (destructor)UIElement_dealloc,/* tp_dealloc */
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
    (getattrofunc)UIElement_getattr, /* tp_getattro */
    (setattrofunc)UIElement_setattr, /* tp_setattro */
    0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "",                     /* tp_doc */
    0,                      /* tp_traverse */
    0,                      /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    UIElement_methods,      /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    (initproc)UIElement_init,/* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

struct Hook_Object
{
    PyObject_HEAD
    Hook impl;
};

static int Hook_init(Hook_Object * self, PyObject * args, PyObject * kwds)
{
    if( ! PyArg_ParseTuple( args, "" ) )
    {
        return -1;
    }
    
    self->impl = Hook::init();

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

struct Console_Object
{
    PyObject_HEAD
};

static int Console_init(Console_Object * self, PyObject * args, PyObject * kwds)
{
    if( ! PyArg_ParseTuple( args, "" ) )
    {
        return -1;
    }
    
    return 0;
}

static void Console_dealloc(Console_Object * self)
{
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject * Console_write(Console_Object * self, PyObject* args)
{
    PyObject * pys;
    if( ! PyArg_ParseTuple(args, "U", &pys ) )
    {
        return NULL;
    }
    
    const char * s = PyUnicode_AsUTF8AndSize(pys, NULL);
    
    Keyhac::Console::write(s);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Console_methods[] = {
    { "write", (PyCFunction)Console_write, METH_STATIC|METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Console_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Console",              /* tp_name */
    sizeof(Console_Type),   /* tp_basicsize */
    0,                      /* tp_itemsize */
    (destructor)Console_dealloc,/* tp_dealloc */
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
    0,                      /* tp_getattro */
    0,                      /* tp_setattro */
    0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "",                     /* tp_doc */
    0,                      /* tp_traverse */
    0,                      /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    Console_methods,        /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    (initproc)Console_init, /* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

static PyObject * _getFocus(PyObject *self, PyObject *args)
{
    std::string focus = "Hello";
    
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
    if( PyType_Ready(&UIElement_Type)<0 ) return NULL;
    if( PyType_Ready(&Console_Type)<0 ) return NULL;

    PyObject *m, *d;

    m = PyModule_Create(&keyhac_core_module);
    if(m == NULL) return NULL;

    Py_INCREF(&Hook_Type);
    PyModule_AddObject( m, "Hook", (PyObject*)&Hook_Type );

    Py_INCREF(&UIElement_Type);
    PyModule_AddObject( m, "UIElement", (PyObject*)&UIElement_Type );
    
    Py_INCREF(&Console_Type);
    PyModule_AddObject( m, "Console", (PyObject*)&Console_Type );
    
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
