//
//  KeyhacCore.hpp
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-10-18.
//

extern "C" {
    struct _object;
    typedef struct _object PyObject;
}

extern const char * keyhacCoreModuleName;
extern PyObject * keyhacCoreModuleInit(void);
