import sys
import keyhac_core

class StandardIo:
    
    def __init__(self, default_stream):
        self.default_stream = default_stream

    def write(self, s):
        keyhac_core.Console.write(s)
        self.default_stream.write(s)

    @staticmethod
    def installRedirection():
        sys.stdout = StandardIo(sys.stdout)
        sys.stderr = StandardIo(sys.stderr)

    @staticmethod
    def uninstallRedirection():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

