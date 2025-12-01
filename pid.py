import os
import sys
import atexit
import signal
import errno
from modules.common.common import set_logger

logger = set_logger()


def _pid_is_running(pid: int) -> bool:
    """Return True if a process with given PID is running, else False."""
    if pid <= 0:
        return False

    if os.name == "nt":
        # Windows-specific check
        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

            OpenProcess = kernel32.OpenProcess
            OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            OpenProcess.restype = wintypes.HANDLE

            GetExitCodeProcess = kernel32.GetExitCodeProcess
            GetExitCodeProcess.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(wintypes.DWORD),
            ]
            GetExitCodeProcess.restype = wintypes.BOOL

            CloseHandle = kernel32.CloseHandle
            CloseHandle.argtypes = [wintypes.HANDLE]
            CloseHandle.restype = wintypes.BOOL

            handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False

            try:
                exit_code = wintypes.DWORD()
                if not GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return False
                return exit_code.value == STILL_ACTIVE
            finally:
                CloseHandle(handle)
        except Exception:
            return False

    else:
        # POSIX check
        try:
            os.kill(pid, 0)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return False  # Process does not exist
            elif e.errno == errno.EPERM:
                return True  # Process exists but no permission
            else:
                return False
        else:
            return True


def ensure_single_instance(pid_file: str):
    """
    Ensure only one instance of this application is running.
    - If PID file exists and PID is running -> exit.
    - If PID file exists but PID is not running -> remove and continue.
    - Write current PID to PID file.
    """
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                content = f.read().strip()
            old_pid = int(content)
        except (OSError, ValueError):
            old_pid = None

        if old_pid and _pid_is_running(old_pid):
            print(f"Another instance is already running with PID {old_pid}. Exiting.")
            sys.exit(1)
        else:
            # Stale PID file -> remove it
            try:
                os.remove(pid_file)
                logger.warning("Removed stale PID file.")
            except OSError:
                pass

    # Write current PID
    pid = os.getpid()
    with open(pid_file, "w") as f:
        f.write(str(pid))
    logger.info(f"PID file created at {pid_file} with PID {pid}")

    # Cleanup PID file on exit
    def _cleanup():
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
                logger.info(f"PID file {pid_file} removed on exit.")
        except OSError:
            pass

    atexit.register(_cleanup)

    # Handle signals for clean exit
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))


# Usage Example
if __name__ == "__main__":
    ensure_single_instance("app.pid")
    try:
        while True:
            pass  # Replace with your actual code
    except KeyboardInterrupt:
        print("Exiting...")
