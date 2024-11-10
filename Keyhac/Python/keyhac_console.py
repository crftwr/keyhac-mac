import sys
import logging
import keyhac_core

class StandardIo:
    
    def __init__(self, default_stream):
        self.default_stream = default_stream

    def write(self, s):
        keyhac_core.Console.write(s)
        self.default_stream.write(s)

    @staticmethod
    def install_redirection():
        sys.stdout = StandardIo(sys.stdout)
        sys.stderr = StandardIo(sys.stderr)

    @staticmethod
    def uninstall_redirection():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class ConsoleLoggingHandler(logging.Handler):

    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            s = self.format(record) + "\n"
            keyhac_core.Console.write(s, record.levelno)
            sys.__stdout__.write(s)
        except:
            self.handleError(record)


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = ConsoleLoggingHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s : %(levelname)s : %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def initializeConsole():

    # for Xcode console
    sys.stdout.reconfigure(encoding='utf-8')

    StandardIo.install_redirection()

