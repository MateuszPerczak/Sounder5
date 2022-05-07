from tkinter import Event
from typing import Callable


class Inspector:
    def __init__(self: object, parent: object) -> object:
        # variables
        self.parent: object = parent
        self.widget: object = None
        self.update_speed: int = 500
        self.run: bool = True
        self.highlighted_widget: list = []
        self.ignore_widgets = ('TProgressbar', 'Progressbar')
        # events
        self.bindings: dict = {'start': [],
                               'end': [], 'change': [], 'pointing': [], }

        parent.after(1000, lambda: self.monitor_widget(parent))

    def start_inspecting(self: object) -> None:
        self.__notify('start')
        self.parent.bind('<Motion>', self.__while_inspecting)
        self.parent.bind('<Button-1>', self.__finish_inspecting)

    def stop_inspecting(self: object) -> None:
        self.parent.unbind('<Motion>')
        self.parent.unbind('<Button-1>')

    def get_widget(self: object) -> object:
        return self.widget

    def set_widget(self: object, widget: object) -> None:
        self.widget = widget
        self.__notify('change')

    def __while_inspecting(self: object, _: Event) -> None:
        position: tuple = self.parent.winfo_pointerxy()
        widget: object = self.parent.winfo_containing(position[0], position[1])
        if widget is not self.widget:
            self.__unhighlight_widget(self.widget)
            self.widget = widget
            self.__highlight_widget(widget)
            self.__notify('pointing')

    def __finish_inspecting(self: object, _: Event) -> None:
        self.__notify('end')
        self.parent.unbind('<Motion>')
        self.parent.unbind('<Button-1>')
        self.__unhighlight_all()

    def get_children(self: object, widget: object) -> list:
        children_list = widget.winfo_children()
        for widget in children_list:
            if widget.winfo_children():
                children_list.extend(widget.winfo_children())
        return children_list

    def bind(self: object, bind_type: str, methode: Callable) -> None:
        self.bindings[bind_type].append(methode)

    def unbind(self: object, methode: Callable) -> None:
        for key in self.bindings:
            if methode in self.bindings[key]:
                self.bindings[key].remove(methode)

    def __notify(self: object, notify_type: str) -> None:
        for methode in self.bindings[notify_type]:
            methode()

    def monitor_widget(self: object, widget: object) -> None:
        widget.bind('<Configure>', lambda _: self.__notify('change'), add='+')
        self.parent.after(1000, self.__update)

    def __update(self: object) -> None:
        if self.run:
            self.__notify('change')
            self.parent.after(self.update_speed, self.__update)

    def unbind_all(self: object) -> None:
        self.run = False
        self.parent.unbind('<Button-1>')
        self.parent.unbind('<Configure>')

    def __highlight_widget(self: object, widget: object) -> None:
        widget_class: str = widget.winfo_class()
        if widget_class not in self.highlighted_widget:
            widget_config: dict = widget.config()
            if 'state' in widget_config:
                self.highlighted_widget.append(widget)
                if widget_class[0] == 'T':
                    widget.state(['disabled'])
                else:
                    widget['state'] = 'disabled'

    def __unhighlight_widget(self: object, widget: object) -> None:
        widget_class: str = widget.winfo_class()
        if widget in self.highlighted_widget:
            widget_config: dict = widget.config()
            if 'state' in widget_config:
                self.highlighted_widget.remove(widget)
                if widget_class[0] == 'T':
                    widget.state(['!disabled'])
                else:
                    widget['state'] = 'normal'

    def __unhighlight_all(self: object) -> None:
        for widget in self.highlighted_widget:
            self.__unhighlight_widget(widget)

    def delete_current_widget(self: object, _: Event = None) -> None:
        if self.widget and self.widget.winfo_class() not in ('Tk', 'Toplevel'):
            widget_parent: object = self.parent._nametowidget(
                self.widget.winfo_parent())
            parent_childrens: list = widget_parent.winfo_children()
            child_index: int = parent_childrens.index(self.widget)
            # delete widget
            parent_childrens.remove(self.widget)
            self.widget.destroy()
            if parent_childrens:
                # select next widget
                self.widget = parent_childrens[child_index - 1]
            else:
                # select parent widget
                self.widget = widget_parent
