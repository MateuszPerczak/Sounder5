from tkinter import Tk, ttk, PhotoImage
from typing import Callable
from ..Components.SystemTheme import get_theme
from os.path import join


class Layout:
    def __init__(self: object, parent: Tk, absolute_path: str) -> object:
        # pass parent object
        self.parent = parent
        # init theme object
        self.parent.layout = ttk.Style(self.parent)
        # abs path
        self.abs_path = absolute_path

        self.parent.layout.layout('debugger.TButton', [('Button.padding', {
                                  'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # treeview
        self.parent.layout.configure('debugger.Treeview', indent=25, rowheight=25, font=(
            'Catamaran', 10, 'bold'))
        self.parent.layout.layout('debugger.Treeview', [('Treeview.treearea', {
            'sticky': 'nswe'})])  # Remove the borders
        self.tree_open = PhotoImage(
            file=join(self.abs_path, r'Resources\\plus.png'))
        self.tree_close = PhotoImage(
            file=join(self.abs_path, r'Resources\\minus.png'))
        self.tree_empty = PhotoImage(
            file=join(self.abs_path, r'Resources\\empty.png'))
        self.parent.layout.element_create('Treeitem.indicator',
                                          'image', self.tree_open, ('user1', '!user2',
                                                                    self.tree_close), ('user2', self.tree_empty),
                                          sticky='w', width=20)
        self.parent.layout.layout('Treeview.Item',
                                  [('Treeitem.padding',
                                    {'sticky': 'nswe',
                                     'children': [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                                                  ('Treeitem.image', {
                                                      'side': 'left', 'sticky': ''}),
                                                  ('Treeitem.text', {
                                                   'side': 'left', 'sticky': ''})
                                                  ]})]
                                  )

        # scrollbar
        self.parent.layout.element_create(
            'debugger.Vertical.Scrollbar.trough', 'from', 'clam')
        self.parent.layout.element_create(
            'debugger.Vertical.Scrollbar.thumb',
            'from', 'clam')
        self.parent.layout.layout('debugger.Vertical.TScrollbar', [('debugger.Vertical.Scrollbar.trough', {'children': [
            ('debugger.Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])


class Theme:
    def __init__(self: object, parent: Tk) -> None:
        # pass parent object
        self.parent = parent
        self.colors: dict = {'Dark': ['#111', '#212121', '#333', '#fff'], 'Light': [
            '#fff', '#ecf0f1', '#ecf0f1', '#000']}
        # get system theme
        self.system_theme: str = get_theme()
        self.colors['System'] = self.colors[self.system_theme]
        # set default applied theme
        self.applied_theme: str = 'Light'
        # bindings
        self.bindings: dict = {'changed': []}

    def apply(self: object, theme: str) -> None:
        self.applied_theme = theme
        # pass parent object
        self.parent.configure(background=self.colors[theme][1])
        # frames
        self.parent.layout.configure(
            'debugger.TFrame', background=self.colors[theme][0])
        self.parent.layout.configure(
            'debugger.dark.TFrame', background=self.colors[theme][1])
        # label
        self.parent.layout.configure('debugger.TLabel', background=self.colors[theme][0], font=(
            'catamaran 12 bold'), foreground=self.colors[theme][3])
        # button
        self.parent.layout.configure('debugger.TButton', background=self.colors[theme][0], font=(
            'catamaran 12 bold'), foreground=self.colors[theme][3], anchor='w', padding=4)

        self.parent.layout.map('debugger.TButton', background=[('pressed', '!disabled', self.colors[theme][1]), (
            'active', self.colors[theme][1]), ('selected', self.colors[theme][1])])

        # treewiev
        self.parent.layout.map('debugger.Treeview', background=[
            ('selected', self.colors[theme][1])], foreground=[('selected', self.colors[theme][3])])

        # scrollbar
        self.parent.layout.configure('debugger.Vertical.TScrollbar', gripcount=0, background=self.colors[theme][2], darkcolor=self.colors[
                                     theme][0], lightcolor=self.colors[theme][0], troughcolor=self.colors[theme][0], bordercolor=self.colors[theme][0])

        self.parent.layout.map('debugger.Vertical.TScrollbar', background=[('pressed', '!disabled', self.colors[theme][2]), (
            'disabled', self.colors[theme][0]), ('active', self.colors[theme][2]), ('!active', self.colors[theme][2])])

        # notify event
        self.__notify('changed')

    def get_theme(self: object) -> str:
        if self.applied_theme == 'System':
            return self.system_theme
        return self.applied_theme

    def get_internal_theme(self: object) -> str:
        return self.applied_theme

    def get_colors(self: object, theme: str) -> list:
        return self.colors[theme]

    def bind(self: object, bind_type: str, methode: Callable) -> None:
        self.bindings[bind_type].append(methode)

    def unbind(self: object, methode: Callable) -> None:
        for key in self.bindings:
            if methode in self.bindings[key]:
                self.bindings[key].remove(methode)

    def __notify(self: object, notify_type: str) -> None:
        for methode in self.bindings[notify_type]:
            methode()
