import sys
import logging
import keyhac_core
from keyhac_const import CONSOLE_STYLE_DEFAULT, CONSOLE_STYLE_ERROR, CONSOLE_STYLE_WARNING


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
            if record.levelno >= logging.ERROR:
                highlight_start = CONSOLE_STYLE_ERROR
                highlight_end   = CONSOLE_STYLE_DEFAULT
            elif record.levelno >= logging.WARNING:
                highlight_start = CONSOLE_STYLE_WARNING
                highlight_end   = CONSOLE_STYLE_DEFAULT
            else:
                highlight_start = ""
                highlight_end   = ""

            s = f"{highlight_start}{self.format(record)}{highlight_end}\n"

            keyhac_core.Console.write(s, record.levelno)
            sys.__stdout__.write(s)
        
        except:
            self.handleError(record)


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = ConsoleLoggingHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def initializeConsole():

    # for Xcode console
    sys.stdout.reconfigure(encoding='utf-8')

    StandardIo.install_redirection()

