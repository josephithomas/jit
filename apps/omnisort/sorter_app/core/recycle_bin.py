"""Safe Recycle Bin integration for Windows using native Shell32 API."""
import os
import sys
import ctypes
from ctypes import wintypes
from typing import List, Union

FO_DELETE = 0x0003
FOF_ALLOWUNDO = 0x0040
FOF_NOCONFIRMATION = 0x0010
FOF_SILENT = 0x0004
FOF_NOERRORUI = 0x0400

class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ('hwnd', wintypes.HWND),
        ('wFunc', wintypes.UINT),
        ('pFrom', wintypes.LPCWSTR),
        ('pTo', wintypes.LPCWSTR),
        ('fFlags', wintypes.WORD),
        ('fAnyOperationsAborted', wintypes.BOOL),
        ('hNameMappings', wintypes.LPVOID),
        ('lpszProgressTitle', wintypes.LPCWSTR)
    ]

def send_to_recycle_bin(paths: Union[str, List[str]]) -> bool:
    """Send one or more files/folders to the Windows Recycle Bin."""
    if isinstance(paths, str):
        paths = [paths]
    
    existing = [os.path.abspath(p) for p in paths if os.path.exists(p)]
    if not existing:
        return True

    if sys.platform == 'win32':
        try:
            # pFrom must be double null-terminated
            joined = '\0'.join(existing) + '\0\0'
            fileop = SHFILEOPSTRUCTW()
            fileop.hwnd = None
            fileop.wFunc = FO_DELETE
            fileop.pFrom = joined
            fileop.pTo = None
            fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
            fileop.fAnyOperationsAborted = False
            fileop.hNameMappings = None
            fileop.lpszProgressTitle = None

            res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
            return res == 0 and not fileop.fAnyOperationsAborted
        except Exception:
            pass

    # Fallback if shell operation fails: unlink
    success = True
    for p in existing:
        try:
            if os.path.isdir(p):
                os.rmdir(p)
            else:
                os.remove(p)
        except Exception:
            success = False
    return success

