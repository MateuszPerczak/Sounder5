from tkinter import ttk, PhotoImage
from os.path import join


class InitPage(ttk.Frame):
    def __init__(self: ttk.Frame, parent: object, props: dict) -> ttk.Frame:
        super().__init__(parent, style='debugger.TFrame')
        # variables
        self.logo: PhotoImage = PhotoImage(
            file=join(props['abs_path'], r'Resources\\icon.png')),
        # ui
        ttk.Label(self, image=self.logo, style='debugger.TLabel').place(
            relx=.5, rely=0.5, anchor='c')
