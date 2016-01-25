import ctypes
import ctypes.wintypes
import time
import threading
import win32con
import os
import sys

class HotkeyThread(threading.Thread):

    user32 = ctypes.windll.user32
    functions = []

    def registerHotkey(self, modifiers, vk, function, parameter):
        self.functions.append((modifiers, vk, function, parameter))
        hotkeyId = len(self.functions) - 1
        
        return hotkeyId
        
    def unregisterHotkey(self, hotkeyId):
        pass
        
    def run(self):
        
        for hotkeyId, (modifiers, vk, function, parameter) in enumerate(self.functions):
            if not self.user32.RegisterHotKey(None, hotkeyId, modifiers, vk):
                raise Exception('Unable to register hot key. error code is: ' + str(ctypes.windll.kernel32.GetLastError()))
 
        try:
            msg = ctypes.wintypes.MSG()
            while self.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    (modifiers, vk, function, parameter) = self.functions[msg.wParam]
                    function()
                     
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageA(ctypes.byref(msg))
        except:
            print(str(sys.exc_info()[1]))
        finally:
            for i in range(0, len(self.functions)):
                self.user32.UnregisterHotKey(None, i)
