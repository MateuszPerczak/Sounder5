from tkinter import Toplevel
from .Pages.InitPage import InitPage
from .Pages.MainPage import MainPage
from .Components.View import Layout, Theme
from .Components.Inspector import Inspector
from os.path import dirname, join


class Debugger(Toplevel):
    def __init__(self: Toplevel, parent: object) -> None:
        super().__init__(parent, name='debugger')
        # variables
        self.parent: object = parent
        self.disallowed_windows: list = [self]
        self.abs_path = dirname(__file__)
        # load layout
        self.custom_layout = Layout(self, self.abs_path)
        # load theme
        self.theme = Theme(self)
        self.theme.apply('Light')
        # inspector object
        self.inspector: Inspector = Inspector(parent)

        # window properties
        self.title(f"Debugging: {self.parent.title()}")
        self.configure(background='#222')
        self.attributes("-topmost", True)
        self.minsize(665, 500)
        self.protocol('WM_DELETE_WINDOW', self.__exit)
        self.iconbitmap(join(self.abs_path, r'Resources\\icon.ico'))
        # binds
        self.parent.unbind('<F12>')
        self.bind('<Escape>', lambda _: self.__exit())
        self.bind('<Delete>', self.inspector.delete_current_widget)
        # display init page
        self.init_page: InitPage = InitPage(
            self, props={'abs_path': self.abs_path})
        self.init_page.pack(fill='both', expand=True)
        # init ui
        self.after(150, self.__init)

    def __init(self: Toplevel) -> None:

        # load parent properties
        self.main_page: MainPage = MainPage(
            self, props={'parent': self.parent, 'disallowed_windows': self.disallowed_windows, 'inspector': self.inspector, 'abs_path': self.abs_path, 'move': self.__move})
        self.init_page.destroy()
        self.main_page.pack(fill='both', expand=True)

    def __exit(self: Toplevel) -> None:
        self.inspector.unbind_all()
        self.destroy()

    def __move(self: Toplevel) -> None:
        # variables
        parent_x: int = self.parent.winfo_x()
        self_width: int = self.winfo_width()
        # move window
        if (parent_x - self_width) <= 0:
            self.geometry(
                f'{self_width}x{self.winfo_height()}+{(parent_x + self.parent.winfo_width()) + 5}+{self.parent.winfo_y()}')
        else:
            self.geometry(
                f'{self_width}x{self.winfo_height()}+{(parent_x - self_width) - 5}+{self.parent.winfo_y()}')
