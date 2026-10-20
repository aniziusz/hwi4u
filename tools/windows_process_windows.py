"""Observe only windows in a disposable test process tree."""
def windows_for_process(parent,title_match='HWI4U TEST'):
    """Only windows belonging to this smoke process's descendants; never another client."""
    import ctypes
    from ctypes import wintypes as W
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);user=ctypes.WinDLL('user32',use_last_error=True)
    class Entry(ctypes.Structure):
        _fields_=[('dwSize',W.DWORD),('cntUsage',W.DWORD),('th32ProcessID',W.DWORD),('th32DefaultHeapID',ctypes.c_size_t),('th32ModuleID',W.DWORD),('cntThreads',W.DWORD),('th32ParentProcessID',W.DWORD),('pcPriClassBase',W.LONG),('dwFlags',W.DWORD),('szExeFile',W.WCHAR*260)]
    kernel.CreateToolhelp32Snapshot.restype=W.HANDLE;kernel.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD]
    kernel.Process32FirstW.argtypes=[W.HANDLE,ctypes.POINTER(Entry)];kernel.Process32NextW.argtypes=kernel.Process32FirstW.argtypes;kernel.CloseHandle.argtypes=[W.HANDLE]
    snapshot=kernel.CreateToolhelp32Snapshot(2,0)
    if snapshot==ctypes.c_void_p(-1).value:raise OSError(ctypes.get_last_error(),'Process snapshot failed')
    parents={};entry=Entry();entry.dwSize=ctypes.sizeof(Entry)
    try:
        valid=kernel.Process32FirstW(snapshot,ctypes.byref(entry))
        while valid:
            parents[entry.th32ProcessID]=entry.th32ParentProcessID;valid=kernel.Process32NextW(snapshot,ctypes.byref(entry))
    finally:kernel.CloseHandle(snapshot)
    descendants={parent}
    while True:
        updated=descendants|{pid for pid,ppid in parents.items() if ppid in descendants}
        if updated==descendants:break
        descendants=updated
    callback=ctypes.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM);found=[]
    user.GetWindowTextW.argtypes=[W.HWND,W.LPWSTR,ctypes.c_int];user.GetWindowThreadProcessId.argtypes=[W.HWND,ctypes.POINTER(W.DWORD)];user.IsWindowVisible.argtypes=[W.HWND];user.EnumWindows.argtypes=[callback,W.LPARAM]
    @callback
    def visit(hwnd,_):
        pid=W.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value in descendants and user.IsWindowVisible(hwnd):
            title=ctypes.create_unicode_buffer(512);user.GetWindowTextW(hwnd,title,512)
            if title.value==title_match:found.append((hwnd,pid.value))
        return True
    user.EnumWindows(visit,0);return found

