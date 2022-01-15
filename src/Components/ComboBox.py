from tkinter import Toplevel, ttk, StringVar, PhotoImage
from typing import Callable


class ComboBox(ttk.Frame):
    def __init__(self: object, parent: object, values: list, default_value: int = 0, image: PhotoImage = None, command: Callable = None) -> None:
        super().__init__(parent)
        self.parent: object = parent
        self.values: list = values
        self.command: Callable = command
        self.value: StringVar = StringVar(value=values[default_value])
        ttk.Button(self, image=image, textvariable=self.value, style='third.TButton',
                   compound='right', command=self.toggle_panel).pack(anchor='c')
        self.init_window()

    def init_window(self: object):
        self.window: Toplevel = Toplevel(self.parent)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.bind('<FocusOut>', lambda _: self.hide())
        self.window.protocol('WM_DELETE_WINDOW', lambda _: self.hide())
        for option in self.values:
            self.add_option(option)

    def add_option(self: object, option: str) -> None:
        ttk.Button(self.window, text=option, command=lambda: self.select_option(
            option), style='third.TButton').pack(anchor='c', fill='x')

    def toggle_panel(self: object) -> None:
        self.window.deiconify()
        # get mouse position
        mouse_pos: tuple = self.parent.winfo_pointerxy()
        # get button class
        button: ttk.Button = self.parent.winfo_containing(
            mouse_pos[0], mouse_pos[1])
        if button:
            button_position: tuple = (
                button.winfo_rootx(), button.winfo_rooty())
            self.window.geometry(
                f'{button.winfo_width()}x{len(self.values) * 38}+{button_position[0]}+{button_position[1] + 38}')
        else:
            self.window.geometry('')
            self.window.geometry(f'+{mouse_pos[0]}+{mouse_pos[1]}')
        self.window.focus_set()

    def select_option(self: object, option: str) -> None:
        self.value.set(option)
        self.window.withdraw()
        self.command(option)

    def hide(self: object) -> None:
        self.window.after(10, self.window.withdraw)
