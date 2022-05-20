'''
Inspire from https://stackoverflow.com/questions/37500076/how-to-enable-windows-console-quickedit-mode-from-python
'''
import msvcrt
import atexit
import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# input flags
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_LINE_INPUT      = 0x0002
ENABLE_ECHO_INPUT      = 0x0004
ENABLE_WINDOW_INPUT    = 0x0008
ENABLE_MOUSE_INPUT     = 0x0010
ENABLE_INSERT_MODE     = 0x0020
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_EXTENDED_FLAGS  = 0x0080

# output flags
ENABLE_PROCESSED_OUTPUT   = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004 # VT100 (Win 10)

def check_zero(result, func, args):    
    if not result:
        err = ctypes.get_last_error()
        if err:
            raise ctypes.WinError(err)
    return args

if not hasattr(wintypes, 'LPDWORD'): # PY2
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

kernel32.GetConsoleMode.errcheck= check_zero
kernel32.GetConsoleMode.argtypes = (
    wintypes.HANDLE,   # _In_  hConsoleHandle
    wintypes.LPDWORD,) # _Out_ lpMode

kernel32.SetConsoleMode.errcheck= check_zero
kernel32.SetConsoleMode.argtypes = (
    wintypes.HANDLE, # _In_  hConsoleHandle
    wintypes.DWORD,) # _Out_ lpMode

def get_console_mode(output=False):
    '''Get the mode of the active console input or output
       buffer. Note that if the process isn't attached to a
       console, this function raises an EBADF IOError.
    '''
    device = r'\\.\CONOUT$' if output else r'\\.\CONIN$'
    with open(device, 'r') as con:
        mode = wintypes.DWORD()
        hCon = msvcrt.get_osfhandle(con.fileno())
        kernel32.GetConsoleMode(hCon, ctypes.byref(mode))
        return mode.value

def set_console_mode(mode, output=False):
    '''Set the mode of the active console input or output
       buffer. Note that if the process isn't attached to a
       console, this function raises an EBADF IOError.
    '''
    device = r'\\.\CONOUT$' if output else r'\\.\CONIN$'
    with open(device, 'r') as con:
        hCon = msvcrt.get_osfhandle(con.fileno())
        kernel32.SetConsoleMode(hCon, mode)

def update_console_mode(flags, mask, output=False, restore=False):
    '''Update a masked subset of the current mode of the active
       console input or output buffer. Note that if the process
       isn't attached to a console, this function raises an
       EBADF IOError.
    '''
    current_mode = get_console_mode(output)
    if current_mode & mask != flags & mask:
        mode = current_mode & ~mask | flags & mask
        set_console_mode(mode, output)
    else:
        restore = False
    if restore:
        atexit.register(set_console_mode, current_mode, output)