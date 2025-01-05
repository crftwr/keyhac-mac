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
#define UIElement_Check(op) PyObject_TypeCheck(op, &UIElement_Type)

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
                
        case UIValueType::cases::int_:
            {
                long i = value.getValueInt();
                pyvalue = PyLong_FromLong(i);
            }
            break;
                
        case UIValueType::cases::float_:
            {
                double f = value.getValueFloat();
                pyvalue = PyFloat_FromDouble(f);
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
                pyvalue = Py_BuildValue( "[ii]", range[0], range[1] );
            }
            break;
                
        case UIValueType::cases::point:
            {
                auto point = value.getValuePoint();
                pyvalue = Py_BuildValue( "[ff]", point[0], point[1] );
            }
            break;
                
        case UIValueType::cases::size:
            {
                auto size = value.getValueSize();
                pyvalue = Py_BuildValue( "[ff]", size[0], size[1] );
            }
            break;
                
        case UIValueType::cases::rect:
            {
                auto rect = value.getValueRect();
                pyvalue = Py_BuildValue( "[ffff]", rect[0], rect[1], rect[2], rect[3] );
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

static PyObject * UIElement_get_focused_application( PyObject * self, PyObject * args )
{
    if( ! PyArg_ParseTuple(args,"") )
        return NULL;
    
    PyObject * pyelm = NULL;
    auto elm = UIElement::getFocusedApplication();
    if(elm)
    {
        pyelm = (PyObject*)_createPyUIElement(elm.get());
    }
    
    if(pyelm)
    {
        return pyelm;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static PyObject * UIElement_get_running_applications( PyObject * self, PyObject * args )
{
    if( ! PyArg_ParseTuple(args,"") )
        return NULL;
    
    PyObject * pyapplications = PyList_New(0);

    auto applications = UIElement::getRunningApplications();
    for( swift::Int i=applications.getStartIndex() ; i<applications.getEndIndex() ; ++i )
    {
        auto application = applications[i];

        PyObject* pyitem = (PyObject*)_createPyUIElement(application);
        PyList_Append( pyapplications, pyitem );
        Py_XDECREF(pyitem);
    }
    
    return pyapplications;
}

static PyObject * UIElement_get_attribute_names(UIElement_Object * self, PyObject * args)
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

static PyObject * UIElement_get_attribute_value(UIElement_Object * self, PyObject * args)
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
    
    // FIXME: handle missing attribute as KeyError
    
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

static PyObject * UIElement_set_attribute_value(UIElement_Object * self, PyObject * args)
{
    PyObject * pyattr_name;
    PyObject * pytype_name;
    PyObject * pyvalue;
    if( ! PyArg_ParseTuple(args, "UUO", &pyattr_name, &pytype_name, &pyvalue) )
    {
        return NULL;
    }
    
    const char * attr_name = PyUnicode_AsUTF8AndSize(pyattr_name, NULL);
    std::string type_name = PyUnicode_AsUTF8AndSize(pytype_name, NULL);

    // FIXME: handle missing attribute as KeyError
    
    if(type_name=="bool")
    {
        if( ! PyBool_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a boolean object.");
            return NULL;
        }
        
        auto value = UIValue::fromBool( pyvalue == Py_True );
        self->impl.setAttributeValue(attr_name, value);
    }
    else if(type_name=="number")
    {
        if( PyFloat_Check(pyvalue) )
        {
            auto value = UIValue::fromFloat( PyFloat_AsDouble(pyvalue) );
            self->impl.setAttributeValue(attr_name, value);
        }
        else if(PyLong_Check(pyvalue))
        {
            auto value = UIValue::fromInt( PyLong_Check(pyvalue) );
            self->impl.setAttributeValue(attr_name, value);
        }
        else
        {
            PyErr_SetString( PyExc_TypeError, "value must be int/float.");
            return NULL;
        }
    }
    else if(type_name=="string")
    {
        if( ! PyUnicode_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a string object.");
            return NULL;
        }
        
        auto value = UIValue::fromString( PyUnicode_AsUTF8AndSize(pyvalue, NULL) );
        self->impl.setAttributeValue(attr_name, value);
    }
    else if(type_name=="range")
    {
        if( ! PySequence_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a sequence object.");
            return NULL;
        }
        
        if( PySequence_Length(pyvalue)!=2 )
        {
            PyErr_SetString( PyExc_TypeError, "length of value must be a 2.");
            return NULL;
        }
        
        auto value = swift::Array<swift::Int>::init();
        for( int i=0 ; i<2 ; ++i )
        {
            PyObject * pyitem = PySequence_GetItem(pyvalue, i);

            if( ! PyLong_Check(pyitem) )
            {
                PyErr_SetString( PyExc_TypeError, "value must be a sequence of int.");
                Py_XDECREF(pyitem);
                return NULL;
            }
            
            value.append(PyLong_AsLong(pyitem));

            Py_XDECREF(pyitem);
        }

        auto uivalue = UIValue::fromRange(value);
        self->impl.setAttributeValue(attr_name, uivalue);
    }
    else if(type_name=="point")
    {
        if( ! PySequence_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a sequence object.");
            return NULL;
        }
        
        if( PySequence_Length(pyvalue)!=2 )
        {
            PyErr_SetString( PyExc_TypeError, "length of value must be a 2.");
            return NULL;
        }
        
        auto value = swift::Array<double>::init();
        for( int i=0 ; i<2 ; ++i )
        {
            PyObject * pyitem = PySequence_GetItem(pyvalue, i);

            if( ! PyNumber_Check(pyitem) )
            {
                PyErr_SetString( PyExc_TypeError, "value must be a sequence of numbers.");
                Py_XDECREF(pyitem);
                return NULL;
            }
            
            value.append(PyFloat_AsDouble(pyitem));

            Py_XDECREF(pyitem);
        }

        auto uivalue = UIValue::fromPoint(value);
        self->impl.setAttributeValue(attr_name, uivalue);
    }
    else if(type_name=="size")
    {
        if( ! PySequence_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a sequence object.");
            return NULL;
        }
        
        if( PySequence_Length(pyvalue)!=2 )
        {
            PyErr_SetString( PyExc_TypeError, "length of value must be a 2.");
            return NULL;
        }
        
        auto value = swift::Array<double>::init();
        for( int i=0 ; i<2 ; ++i )
        {
            PyObject * pyitem = PySequence_GetItem(pyvalue, i);

            if( ! PyNumber_Check(pyitem) )
            {
                PyErr_SetString( PyExc_TypeError, "value must be a sequence of numbers.");
                Py_XDECREF(pyitem);
                return NULL;
            }
            
            value.append(PyFloat_AsDouble(pyitem));

            Py_XDECREF(pyitem);
        }

        auto uivalue = UIValue::fromSize(value);
        self->impl.setAttributeValue(attr_name, uivalue);
    }
    else if(type_name=="rect")
    {
        if( ! PySequence_Check(pyvalue) )
        {
            PyErr_SetString( PyExc_TypeError, "value must be a sequence object.");
            return NULL;
        }
        
        if( PySequence_Length(pyvalue)!=4 )
        {
            PyErr_SetString( PyExc_TypeError, "length of value must be a 4.");
            return NULL;
        }
        
        auto value = swift::Array<double>::init();
        for( int i=0 ; i<4 ; ++i )
        {
            PyObject * pyitem = PySequence_GetItem(pyvalue, i);

            if( ! PyNumber_Check(pyitem) )
            {
                PyErr_SetString( PyExc_TypeError, "value must be a sequence of numbers.");
                Py_XDECREF(pyitem);
                return NULL;
            }
            
            value.append(PyFloat_AsDouble(pyitem));

            Py_XDECREF(pyitem);
        }

        auto uivalue = UIValue::fromRect(value);
        self->impl.setAttributeValue(attr_name, uivalue);
    }
    else
    {
        PyErr_SetString( PyExc_ValueError, "unknown or unsupported type");
        return NULL;
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * UIElement_get_action_names(UIElement_Object * self, PyObject * args)
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

static PyObject * UIElement_perform_action(UIElement_Object * self, PyObject * args)
{
    PyObject * pyaction;
    if( ! PyArg_ParseTuple(args, "U", &pyaction ) )
    {
        return NULL;
    }
    
    const char * action = PyUnicode_AsUTF8AndSize(pyaction, NULL);
    
    self->impl.performAction(action);
    
    // FIXME: handle error
    // FIXME: handle missing attribute as KeyError

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef UIElement_methods[] = {
    { "get_focused_application", (PyCFunction)UIElement_get_focused_application, METH_STATIC|METH_VARARGS, "" },
    { "get_running_applications", (PyCFunction)UIElement_get_running_applications, METH_STATIC|METH_VARARGS, "" },
    { "get_attribute_names", (PyCFunction)UIElement_get_attribute_names, METH_VARARGS, "" },
    { "get_attribute_value", (PyCFunction)UIElement_get_attribute_value, METH_VARARGS, "" },
    { "set_attribute_value", (PyCFunction)UIElement_set_attribute_value, METH_VARARGS, "" },
    { "get_action_names", (PyCFunction)UIElement_get_action_names, METH_VARARGS, "" },
    { "perform_action", (PyCFunction)UIElement_perform_action, METH_VARARGS, "" },

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

extern PyTypeObject Clipboard_Type;
#define Clipboard_Check(op) PyObject_TypeCheck(op, &Clipboard_Type)

struct Clipboard_Object
{
    PyObject_HEAD
    Clipboard impl;
};

static int Clipboard_init(Clipboard_Object * self, PyObject * args, PyObject * kwds)
{
    if( ! PyArg_ParseTuple( args, "" ) )
    {
        return -1;
    }
    
    self->impl = Clipboard::init();

    return 0;
}

static void Clipboard_dealloc(Clipboard_Object * self)
{
    self->impl.~Clipboard();

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject * Clipboard_destroy(Clipboard_Object * self, PyObject* args)
{
    if(!PyArg_ParseTuple(args, ""))
    {
        return NULL;
    }
    
    self->impl.destroy();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Clipboard_get_string(Clipboard_Object * self, PyObject* args)
{
    if(!PyArg_ParseTuple(args, ""))
    {
        return NULL;
    }

    auto wrapped_s = self->impl.getString();
    if(wrapped_s.isSome())
    {
        std::string s = wrapped_s.get();

        PyObject * pys = Py_BuildValue( "s", s.c_str() );
        return pys;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static PyObject * Clipboard_set_string(Clipboard_Object * self, PyObject* args)
{
    PyObject * pys;
    
    if(!PyArg_ParseTuple(args, "U", &pys))
    {
        return NULL;
    }

    const char * s = PyUnicode_AsUTF8AndSize(pys, NULL);
    
    self->impl.setString(s);

    Py_INCREF(Py_None);
    return Py_None;
}

static Clipboard_Object * Clipboard_getCurrent(Clipboard_Object * self, PyObject* args)
{
    if(!PyArg_ParseTuple(args, ""))
    {
        return NULL;
    }
    
    auto clipboard = Clipboard::getCurrent();

    Clipboard_Object * pyclipboard = (Clipboard_Object*)Clipboard_Type.tp_alloc(&Clipboard_Type, 0);
    pyclipboard->impl = clipboard;

    return pyclipboard;
}

static PyObject * Clipboard_setCurrent(Clipboard_Object * self, PyObject* args)
{
    Clipboard_Object * pyclipboard;
    if(!PyArg_ParseTuple(args, "O", &pyclipboard))
    {
        return NULL;
    }
    
    if(!Clipboard_Check(pyclipboard))
    {
        PyErr_SetString( PyExc_TypeError, "value must be a Clipboard object.");
        return NULL;
    }

    Clipboard::setCurrent(pyclipboard->impl);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Clipboard_methods[] = {
    { "destroy", (PyCFunction)Clipboard_destroy, METH_VARARGS, "" },
    { "get_string", (PyCFunction)Clipboard_get_string, METH_VARARGS, "" },
    { "set_string", (PyCFunction)Clipboard_set_string, METH_VARARGS, "" },
    { "get_current", (PyCFunction)Clipboard_getCurrent, METH_STATIC|METH_VARARGS, "" },
    { "set_current", (PyCFunction)Clipboard_setCurrent, METH_STATIC|METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Clipboard_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Clipboard",            /* tp_name */
    sizeof(Clipboard_Type), /* tp_basicsize */
    0,                      /* tp_itemsize */
    (destructor)Clipboard_dealloc,/* tp_dealloc */
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
    Clipboard_methods,      /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    (initproc)Clipboard_init,/* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

struct Hook_Object
{
    PyObject_HEAD
    //Hook impl;
};

static PyObject * Hook_set_callback(Hook_Object * self, PyObject* args)
{
    PyObject * pyname;
    PyObject * pycallback;
    if( ! PyArg_ParseTuple(args, "UO", &pyname, &pycallback ) )
    {
        return NULL;
    }
    
    const char * name = PyUnicode_AsUTF8AndSize(pyname, NULL);
    printf("Hook_set_callback - %s\n", name);
    
    if(pycallback!=Py_None)
    {
        auto callback = swift::Optional<PyObjectPtr>::some(PyObjectPtr(pycallback));
        Hook::getInstance().setCallback(name, callback);
    }
    else
    {
        auto callback = swift::Optional<PyObjectPtr>::none();
        Hook::getInstance().setCallback(name, callback);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Hook_send_keyboard_event(Hook_Object * self, PyObject* args)
{
    PyObject * pytype;
    int keyCode;
    if( ! PyArg_ParseTuple(args, "UI", &pytype, &keyCode ) )
    {
        return NULL;
    }
    
    const char * type = PyUnicode_AsUTF8AndSize(pytype, NULL);
    
    Hook::getInstance().sendKeyboardEvent(type, keyCode);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Hook_get_keyboard_layout(Hook_Object * self, PyObject* args)
{
    if( ! PyArg_ParseTuple(args, "" ) )
    {
        return NULL;
    }
    
    std::string layout = Hook::getInstance().getKeyboardLayout();

    PyObject * pylayout = Py_BuildValue( "s", layout.c_str() );
    return pylayout;
}

static PyObject * Hook_acquire_lock(Hook_Object * self, PyObject* args)
{
    if( ! PyArg_ParseTuple(args, "" ) )
    {
        return NULL;
    }
    
    Hook::getInstance().acquireLock();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Hook_release_lock(Hook_Object * self, PyObject* args)
{
    if( ! PyArg_ParseTuple(args, "" ) )
    {
        return NULL;
    }
    
    Hook::getInstance().releaseLock();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Hook_methods[] = {
    { "set_callback", (PyCFunction)Hook_set_callback, METH_STATIC|METH_VARARGS, "" },
    { "send_keyboard_event", (PyCFunction)Hook_send_keyboard_event, METH_STATIC|METH_VARARGS, "" },
    { "get_keyboard_layout", (PyCFunction)Hook_get_keyboard_layout, METH_STATIC|METH_VARARGS, "" },
    { "acquire_lock", (PyCFunction)Hook_acquire_lock, METH_STATIC|METH_VARARGS, "" },
    { "release_lock", (PyCFunction)Hook_release_lock, METH_STATIC|METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Hook_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Hook",                 /* tp_name */
    sizeof(Hook_Type),      /* tp_basicsize */
    0,                      /* tp_itemsize */
    0,                      /* tp_dealloc */
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
    Hook_methods,           /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    0,                      /* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

struct Console_Object
{
    PyObject_HEAD
};

static PyObject * Console_write(Console_Object * self, PyObject* args)
{
    PyObject * pymsg;
    int log_level = 100;

    if( ! PyArg_ParseTuple(args, "U|i", &pymsg, &log_level ) )
    {
        return NULL;
    }
    
    const char * msg = PyUnicode_AsUTF8AndSize(pymsg, NULL);
    
    Keyhac::Console::getInstance().write(msg, log_level);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Console_set_text(Console_Object * self, PyObject* args)
{
    PyObject * pyname;
    PyObject * pytext;
    if( ! PyArg_ParseTuple(args, "UU", &pyname, &pytext) )
    {
        return NULL;
    }
    
    const char * name = PyUnicode_AsUTF8AndSize(pyname, NULL);
    const char * text = PyUnicode_AsUTF8AndSize(pytext, NULL);

    Keyhac::Console::getInstance().setText(name, text);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Console_methods[] = {
    { "write", (PyCFunction)Console_write, METH_STATIC|METH_VARARGS, "" },
    { "set_text", (PyCFunction)Console_set_text, METH_STATIC|METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Console_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Console",              /* tp_name */
    sizeof(Console_Type),   /* tp_basicsize */
    0,                      /* tp_itemsize */
    0,                      /* tp_dealloc */
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
    0,                      /* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------


extern PyTypeObject Chooser_Type;
#define Chooser_Check(op) PyObject_TypeCheck(op, &Chooser_Type)

struct Chooser_Object
{
    PyObject_HEAD
    Chooser impl;
};

static int Chooser_init(Chooser_Object * self, PyObject * args, PyObject * kwds)
{
    PyObject * pyname;
    PyObject * pyitems;
    PyObject * pyselected;
    PyObject * pycanceled;

    if( ! PyArg_ParseTuple(args, "UOOO", &pyname, &pyitems, &pyselected, &pycanceled ) )
    {
        return NULL;
    }
    
    const char * name = PyUnicode_AsUTF8AndSize(pyname, NULL);
    
    if( ! PySequence_Check(pyitems) )
    {
        PyErr_SetString( PyExc_TypeError, "items must be a sequence object.");
        return NULL;
    }
    
    auto items = swift::Array<ChooserItem>::init();
    for( int i=0 ; i<PySequence_Length(pyitems) ; ++i )
    {
        PyObject * pyitem = PySequence_GetItem(pyitems, i);
        
        if( ! PySequence_Check(pyitem) )
        {
            PyErr_SetString( PyExc_TypeError, "each item must be a tuple.");
            Py_XDECREF(pyitem);
            return NULL;
        }
        
        if( PySequence_Length(pyitem) < 3 )
        {
            PyErr_SetString( PyExc_TypeError, "item must be a tuple of >=3 elements.");
            Py_XDECREF(pyitem);
            return NULL;
        }
        
        PyObject * pyicon = PySequence_GetItem(pyitem, 0);
        PyObject * pytext = PySequence_GetItem(pyitem, 1);
        PyObject * pyuuid = PySequence_GetItem(pyitem, 2);

        if( !PyUnicode_Check(pyicon) || !PyUnicode_Check(pytext) || !PyUnicode_Check(pyuuid) )
        {
            PyErr_SetString( PyExc_TypeError, "first 3 elements in item must be strings.");
            Py_XDECREF(pyitem);
            Py_XDECREF(pyicon);
            Py_XDECREF(pytext);
            Py_XDECREF(pyuuid);
            return NULL;
        }

        const char * icon = PyUnicode_AsUTF8AndSize(pyicon, NULL);
        const char * text = PyUnicode_AsUTF8AndSize(pytext, NULL);
        const char * uuid = PyUnicode_AsUTF8AndSize(pyuuid, NULL);

        items.append(ChooserItem::init(icon, text, uuid));
    }

    auto onSelected = PyObjectPtr(pyselected);
    auto onCanceled = PyObjectPtr(pycanceled);
    
    self->impl = Chooser::init(name, items, onSelected, onCanceled);
    
    return 0;
}

static void Chooser_dealloc(Chooser_Object * self)
{
    self->impl.~Chooser();

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject * Chooser_open(Chooser_Object * self, PyObject* args)
{
    int x,y,width,height;
    
    if( ! PyArg_ParseTuple(args, "(iiii)", &x, &y, &width, &height) )
    {
        return NULL;
    }
    
    self->impl.open(x, y, width, height);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * Chooser_destroy(Chooser_Object * self, PyObject* args)
{
    if( ! PyArg_ParseTuple(args, "" ) )
    {
        return NULL;
    }
    
    self->impl.destroy();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Chooser_methods[] = {
    { "open", (PyCFunction)Chooser_open, METH_VARARGS, "" },
    { "destroy", (PyCFunction)Chooser_destroy, METH_VARARGS, "" },
    {NULL,NULL}
};

PyTypeObject Chooser_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Chooser",              /* tp_name */
    sizeof(Chooser_Type),   /* tp_basicsize */
    0,                      /* tp_itemsize */
    (destructor)Chooser_dealloc,/* tp_dealloc */
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
    Chooser_methods,        /* tp_methods */
    0,                      /* tp_members */
    0,                      /* tp_getset */
    0,                      /* tp_base */
    0,                      /* tp_dict */
    0,                      /* tp_descr_get */
    0,                      /* tp_descr_set */
    0,                      /* tp_dictoffset */
    (initproc)Chooser_init, /* tp_init */
    0,                      /* tp_alloc */
    PyType_GenericNew,      /* tp_new */
    0,                      /* tp_free */
};


// ------------------------------------------

static PyMethodDef keyhac_core_methods[] = {
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
    if( PyType_Ready(&Clipboard_Type)<0 ) return NULL;
    if( PyType_Ready(&UIElement_Type)<0 ) return NULL;
    if( PyType_Ready(&Console_Type)<0 ) return NULL;
    if( PyType_Ready(&Chooser_Type)<0 ) return NULL;

    PyObject *m, *d;

    m = PyModule_Create(&keyhac_core_module);
    if(m == NULL) return NULL;

    Py_INCREF(&Hook_Type);
    PyModule_AddObject( m, "Hook", (PyObject*)&Hook_Type );

    Py_INCREF(&Clipboard_Type);
    PyModule_AddObject( m, "Clipboard", (PyObject*)&Clipboard_Type );

    Py_INCREF(&UIElement_Type);
    PyModule_AddObject( m, "UIElement", (PyObject*)&UIElement_Type );
    
    Py_INCREF(&Console_Type);
    PyModule_AddObject( m, "Console", (PyObject*)&Console_Type );
    
    Py_INCREF(&Chooser_Type);
    PyModule_AddObject( m, "Chooser", (PyObject*)&Chooser_Type );
    
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
