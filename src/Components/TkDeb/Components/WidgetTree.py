from tkinter import ttk, PhotoImage, Event
from os.path import join
from typing import Callable


class WidgetTree(ttk.Frame):
    def __init__(self: ttk.Frame, parent: object, disallowed_windows: list, abs_path: str) -> ttk.Frame:
        super().__init__(parent, style='debugger.TFrame')
        # variables
        self.disallowed_windows: list = disallowed_windows
        self.target_tree: dict = {}
        self.abs_path: str = abs_path
        self.last_target: object = None

        self.bindings: dict = {'select': []}
        # ui

        self.icons: dict = {
            'Tk': PhotoImage(file=join(self.abs_path, r'Resources\\app.png')),
            'TFrame': PhotoImage(file=join(self.abs_path, r'Resources\\frame.png')),
            'TButton': PhotoImage(file=join(self.abs_path, r'Resources\\button.png')),
            'TLabel': PhotoImage(file=join(self.abs_path, r'Resources\\label.png')),
            'TEntry': PhotoImage(file=join(self.abs_path, r'Resources\\entry.png')),
            'TRadiobutton': PhotoImage(file=join(self.abs_path, r'Resources\\radiobutton.png')),
            'TCombobox': PhotoImage(file=join(self.abs_path, r'Resources\\combobox.png')),
            'TScale': PhotoImage(file=join(self.abs_path, r'Resources\\scale.png')),
            'TProgressbar': PhotoImage(file=join(self.abs_path, r'Resources\\progress.png')),
            'TCheckbutton': PhotoImage(file=join(self.abs_path, r'Resources\\checkbox.png')),
            'Treeview': PhotoImage(file=join(self.abs_path, r'Resources\\tree.png')),
            'Unknown': PhotoImage(file=join(self.abs_path, r'Resources\\unknown.png')),
        }
        self.icons['Toplevel'] = self.icons['Tk']

        ttk.Label(self, text='Widgets tree', style='debugger.TLabel').pack(
            side='top', fill='x', padx=10, pady=(10, 5))
        mid_frame: ttk.Frame = ttk.Frame(self, style='debugger.TFrame')
        # tree
        self.tree_view: ttk.Treeview = ttk.Treeview(
            mid_frame, style='debugger.Treeview', show="tree")

        # disable any interactoins with the tree
        self.tree_view.bind('<Motion>', 'break')
        self.tree_view.bind('<ButtonRelease-1>',
                            lambda _: self.__notify('select'))
        # pack tree
        self.tree_view.pack(side='left', fill='both',
                            expand=True, padx=10, pady=10)
        # scrollbar
        self.tree_scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            mid_frame, orient='vertical', command=self.tree_view.yview, style='debugger.Vertical.TScrollbar')
        self.tree_view.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.pack(side='left', fill='y')

        mid_frame.pack(side='top', fill='both', expand=True)

    def generate_tree(self: ttk.Frame, target: object) -> None:
        self.tree_view.delete(*self.tree_view.get_children())
        target_id: int = target.winfo_id()
        self.tree_view.insert('', 'end', text=target.winfo_class(),
                              iid=target_id, open=False, image=self.icons['Tk'], value=target)
        self.target_tree[target] = {
            'children': self.__find_children(target), 'name': target.winfo_class().upper(), 'id': target_id}
        self.last_target = target

    def __find_children(self: ttk.Frame, widget: object) -> None:
        childs: list = []
        for child in widget.winfo_children():
            if child in self.disallowed_windows:
                continue
            widget_class: str = child.winfo_class()
            child_id: int = child.winfo_id()
            self.tree_view.insert(
                widget.winfo_id(), 'end', text=f"{widget_class}".upper(), iid=child_id, value=child, open=False, image=self.icons[widget_class if widget_class in self.icons else 'Unknown'])
            childs.append(child)
            self.target_tree[child] = {'children': self.__find_children(
                child), 'name': widget_class, 'id': child_id}

        return childs

    def highlight_widget(self: ttk.Frame, widget: object) -> None:
        if widget:
            widget_id: str = widget.winfo_id()
            if widget in self.target_tree:
                self.tree_view.selection_set(widget_id)
                self.tree_view.see(widget_id)

    def get_widget(self: ttk.Frame) -> object:
        iid: str = self.tree_view.focus()
        if iid:
            widget = self.tree_view.item(iid)['values'][0]
            return self.nametowidget(widget)

    def bind(self: object, bind_type: str, methode: Callable) -> None:
        self.bindings[bind_type].append(methode)

    def unbind(self: object, methode: Callable) -> None:
        for key in self.bindings:
            if methode in self.bindings[key]:
                self.bindings[key].remove(methode)

    def __notify(self: object, notify_type: str) -> None:
        for methode in self.bindings[notify_type]:
            methode(self.get_widget())
