from tkinter import ttk, PhotoImage, StringVar
from ..Components.WidgetTree import WidgetTree
from ..Components.WidgetProperties import WidgetProperties
from os.path import join


class MainPage(ttk.Frame):
    def __init__(self: ttk.Frame, parent: object, props: dict) -> ttk.Frame:
        super().__init__(parent, style='debugger.dark.TFrame')
        # variables
        self.parent: object = props['parent']
        self.disallowed_windows: list = props['disallowed_windows']
        self.inspecting: bool = False
        self.inspector: object = props['inspector']
        self.abs_path = props['abs_path']
        self.pinned: bool = False
        self.__move = props['move']
        self.num_of_widgets: int = len(
            self.inspector.get_children(self.parent))
        # widgets counter
        self.widgets_counter: StringVar = StringVar(
            value=f"{self.num_of_widgets} ")

        # icons

        self.icons = {
            'inspect': [PhotoImage(file=join(self.abs_path, r'Resources\\start_inspection.png')), PhotoImage(file=join(self.abs_path, r'Resources\\end_inspection.png'))],
            'widgets': PhotoImage(file=join(self.abs_path, r'Resources\\widgets.png')),
            'pin': [PhotoImage(file=join(self.abs_path, r'Resources\\pin.png')), PhotoImage(file=join(self.abs_path, r'Resources\\unpin.png'))],
            'delete': PhotoImage(file=join(self.abs_path, r'Resources\\delete.png')),
        }

        # ui
        top_frame: ttk.Frame = ttk.Frame(self, style='debugger.dark.TFrame')
        # inspect button
        self.inspect_button: ttk.Button = ttk.Button(
            top_frame, image=self.icons['inspect'][self.inspecting], command=self.toggle_inspection, style='debugger.TButton')
        self.inspect_button.pack(side='left', padx=10)
        # widgets label
        ttk.Label(
            top_frame, image=self.icons['widgets'], textvariable=self.widgets_counter, style='debugger.TLabel', compound='left').pack(side='left', padx=(0, 10), fill='y')
        # pin bytton
        self.pin_button: ttk.Button = ttk.Button(
            top_frame, image=self.icons['pin'][self.pinned], command=self.pin_window, style='debugger.TButton')
        self.pin_button.pack(side='left', padx=(0, 10))
        ttk.Button(
            top_frame, image=self.icons['delete'], command=self.inspector.delete_current_widget, style='debugger.TButton').pack(side='left', padx=(0, 10))

        top_frame.pack(side='top', fill='x', pady=10)
        # middle frame
        mid_frame: ttk.Frame = ttk.Frame(self, style='debugger.dark.TFrame')
        # treeview
        self.widget_tree: WidgetTree = WidgetTree(
            mid_frame, self.disallowed_windows, self.abs_path)
        # self.widget_tree.pack(side='left', fill='both', padx=10)
        self.widget_tree.place(relx=0, y=0, relwidth=0.4, relheight=1)
        # widget props
        self.widget_props: WidgetProperties = WidgetProperties(mid_frame)
        # self.widget_props.pack(side='left', fill='both', padx=(0, 10))
        self.widget_props.place(relx=.4, y=0, relwidth=0.6, relheight=1)
        # pack mid frame
        mid_frame.pack(side='top', fill='both',
                       expand=True, pady=(0, 10), padx=10)

        ttk.Label(self, text=' TkDeb by Mateusz Perczak',
                  style='debugger.TLabel').pack(side='left', fill='x', expand=True, pady=(0, 10), padx=10)
        # generate tree
        self.widget_tree.generate_tree(self.parent)
        self.widget_tree.bind('select', self.select)
        # bind events
        self.inspector.bind('pointing', self.highlight_widget)
        self.inspector.bind('end', self.end_inspection)
        self.inspector.bind('change', self.update)
        # select widget
        self.select(self.parent)

    def highlight_widget(self: ttk.Frame) -> None:
        widget: object = self.inspector.get_widget()
        self.widget_tree.highlight_widget(widget)
        self.widget_props.load_properties(widget)

    def toggle_inspection(self: ttk.Frame) -> None:
        if self.inspecting:
            self.end_inspection()
        else:
            self.prepare_inspection()

    def prepare_inspection(self: ttk.Frame) -> None:
        self.inspecting = True
        self.inspector.start_inspecting()
        self.update_inspect_button()

    def end_inspection(self: ttk.Frame) -> None:
        self.inspecting = False
        self.update_inspect_button()
        self.inspector.stop_inspecting()
        self.widget_props.load_properties(self.inspector.get_widget())

    def update_inspect_button(self: ttk.Frame) -> None:
        self.inspect_button.config(
            image=self.icons['inspect'][self.inspecting])

    def pin_window(self: ttk.Frame) -> None:
        self.pinned = not self.pinned
        if self.pinned:
            self.__move()
            self.inspector.bind('change', self.__move)
        else:
            self.inspector.unbind(self.__move)
        self.pin_button.config(image=self.icons['pin'][self.pinned])

    def update(self: ttk.Frame) -> None:
        num_of_widgets: int = len(self.inspector.get_children(self.parent))
        widget: object = self.inspector.get_widget()
        if self.num_of_widgets != num_of_widgets:
            self.num_of_widgets = num_of_widgets
            self.widget_tree.generate_tree(self.parent)
            self.widget_tree.highlight_widget(widget)
            self.widgets_counter.set(f"{self.num_of_widgets} ")
        if widget:
            self.widget_props.load_properties(widget)

    def select(self: ttk.Frame, widget: object) -> None:
        old_widget = self.inspector.get_widget()
        if old_widget != widget:
            self.inspector.widget = widget
            self.widget_props.load_properties(widget)
