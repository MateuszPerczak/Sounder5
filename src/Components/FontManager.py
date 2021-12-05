from os.path import join, basename, splitext, exists
from os import environ, remove
from shutil import copy
from winreg import OpenKey, KEY_SET_VALUE, SetValueEx, HKEY_LOCAL_MACHINE, REG_SZ
from ctypes import wintypes, WinDLL, POINTER, c_wchar, byref, sizeof


class FontManager:

    def __init__(self: object) -> None:
        # do init stuff here
        # this stuff it's not mine 

        self.user32 = WinDLL('user32', use_last_error=True)
        self.gdi32 = WinDLL('gdi32', use_last_error=True)

        if not hasattr(wintypes, 'LPDWORD'):
            wintypes.LPDWORD = POINTER(wintypes.DWORD)

        self.user32.SendMessageTimeoutW.restype = wintypes.LPVOID
        self.user32.SendMessageTimeoutW.argtypes = (
            wintypes.HWND,   # hWnd
            wintypes.UINT,   # Msg
            wintypes.LPVOID, # wParam
            wintypes.LPVOID, # lParam
            wintypes.UINT,   # fuFlags
            wintypes.UINT,   # uTimeout
            wintypes.LPVOID) # lpdwResult

        self.gdi32.AddFontResourceW.argtypes = (wintypes.LPCWSTR,) # lpszFilename

        # http://www.undocprint.org/winspool/getfontresourceinfo
        self.gdi32.GetFontResourceInfoW.argtypes = (
            wintypes.LPCWSTR, # lpszFilename
            wintypes.LPDWORD, # cbBuffer
            wintypes.LPVOID,  # lpBuffer
            wintypes.DWORD)   # dwQueryType


    def install_font(self: object, path: str):
        # copy the font to the Windows Fonts folder
        dst_path = join(environ['SystemRoot'], 'Fonts', basename(path))
        if not exists(dst_path):
            copy(path, dst_path)
            # load the font in the current session
            if not self.gdi32.AddFontResourceW(dst_path):
                remove(dst_path)
                raise WindowsError('AddFontResource failed to load "%s"' % path)
            # notify running programs
            self.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0x0002, 1000, None)
            # store the fontname/filename in the registry
            filename = basename(dst_path)
            fontname = splitext(filename)[0]
            # try to get the font's real name
            cb = wintypes.DWORD()
            if self.gdi32.GetFontResourceInfoW(filename, byref(cb), None, 1):
                buf = (c_wchar * cb.value)()
                if self.gdi32.GetFontResourceInfoW(filename, byref(cb), buf, 1):
                    fontname = buf.value
            is_truetype = wintypes.BOOL()

            cb.value = sizeof(is_truetype)

            self.gdi32.GetFontResourceInfoW(filename, byref(cb), byref(is_truetype), 3)
            
            if is_truetype:
                fontname += ' (TrueType)'

            with OpenKey(HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows NT\CurrentVersion\Fonts', 0, KEY_SET_VALUE) as key:
                SetValueEx(key, fontname, 0, REG_SZ, filename)


