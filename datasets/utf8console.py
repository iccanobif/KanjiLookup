import sys, ctypes, atexit, io

def _module():

    if sys.platform != "win32":
        return
        
    originalOutputCP = ctypes.windll.kernel32.GetConsoleOutputCP()
    originalCP = ctypes.windll.kernel32.GetConsoleCP()

    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)

    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf8", line_buffering=True)
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf8", line_buffering=True)

    def restoreCP():
        ctypes.windll.kernel32.SetConsoleOutputCP(originalOutputCP)
        ctypes.windll.kernel32.SetConsoleCP(originalCP)

    atexit.register(restoreCP)
    
_module()