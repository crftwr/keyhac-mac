import os
import shutil
import traceback

class Config:

    def __init__(self, filename, default_config_filename):
        
        self.filename = filename
        self.config_namespace = {}

        if not os.path.exists(filename):
            os.makedirs( os.path.dirname(filename), exist_ok=True )
            shutil.copyfile(default_config_filename, filename)

        self.reload()

    def reload(self):
        
        try:
            fd = open(self.filename, "rb")
            fileimage = fd.read()
            self.config_namespace = {}
            compiled_code = compile(fileimage, os.path.basename(self.filename), "exec")
            exec(compiled_code, self.config_namespace, self.config_namespace)
        except:
            traceback.print_exc()

    def call(self, funcname, *args):

        try:
            func = self.config_namespace[funcname]
        except KeyError:
            return

        try:
            func(*args)
        except:
            traceback.print_exc()
