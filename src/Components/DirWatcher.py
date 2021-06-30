import win32file
import win32con
from time import sleep
from os.path import join

class DirWatcher(object):
    def __init__(self, path: str, update_time: float) -> None:
        self.path: str = path
        self.update_time: float = update_time
        self.init_watcher()

    def init_watcher(self) -> None:
        watcher = win32file.CreateFile(self.path, 0x0001, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE, None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)
        while True:
            for action, song in win32file.ReadDirectoryChangesW(watcher, 1024, True, win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | win32con.FILE_NOTIFY_CHANGE_SIZE | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | win32con.FILE_NOTIFY_CHANGE_SECURITY, None, None):
                if song.endswith(('.mp3', '.flac', '.ogg')) and action == 2:
                    self.on_delete(join(self.path, song))
            sleep(self.update_time)

    def on_delete(self, song: str) -> None: pass