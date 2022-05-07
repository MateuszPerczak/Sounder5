from tkinter import ttk, Listbox
from .Matcher import Matcher


class WidgetProperties(ttk.Frame):
    def __init__(self: ttk.Frame, parent: object) -> ttk.Frame:
        super().__init__(parent, style='debugger.TFrame')
        # variables
        self.matcher: object = Matcher()
        # ui
        ttk.Label(self, text="Widget properties", style='debugger.TLabel').pack(
            side='top', padx=10, fill='x', pady=(10, 5))

        self.list_box: Listbox = Listbox(
            self, bd=0, activestyle="none", takefocus=False, selectmode="SINGLE", highlightthickness=0, font=(
                'Catamaran', 11, 'bold'), selectbackground='#fff', selectforeground='#000')
        self.list_box.pack(side='left', fill='both', expand=True, padx=10)

        # scrollbar
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self, orient='vertical', command=self.list_box.yview, style='debugger.Vertical.TScrollbar')
        self.list_box.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='left', fill='y')

    def load_properties(self: object, widget: object) -> None:
        if widget:
            scroll_pos = self.list_box.yview()[0]
            self.list_box.delete(0, 'end')
            properties: dict = self.matcher.match(widget)
            for key in properties:
                self.list_box.insert('end', f'{key}: {properties[key]}')
            self.list_box.yview_moveto(scroll_pos)
