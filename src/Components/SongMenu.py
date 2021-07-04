try:
    from tkinter import Toplevel, ttk
    from time import sleep
except ImportError as err:
    exit(err)

class SongMenu(Toplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        # expose variables to this class
        self.parent = parent
        self.playlists: dict = parent.settings['playlists']
        self.icons: dict = parent.icons
        self.playlist_menu = parent.menu_playlist
        # variables
        self.playlist_panels: dict = {}
        self.animation = None
        self.song: str = ''
        self.disabled_playlists: list = []
        # hide window
        self.withdraw()
        # configure window
        self.overrideredirect(True)
        self.protocol('WM_DELETE_WINDOW', self.hide())
        self.bind('<FocusOut>', lambda _:self.hide())
        self.configure(background=parent['background'])
        self.init_ui()

    def init_ui(self) -> None:
        # add playlist and append song
        ttk.Button(self, image=self.icons['plus'], text='Add playlist', compound='left', command=self.add_playlist).pack(side='top', fill='x', padx=5, pady=(5, 5))
        # playlist buttons
        self.playlist_panel = ttk.Frame(self)
        for playlist in self.playlists:
            if playlist != 'Favorites':
                self.playlist_panels[playlist] = ttk.Button(self.playlist_panel, image=self.icons['playlist'][0], text=self.playlists[playlist]['Name'], compound='left', command=lambda: self.add_to_playlist(playlist))
                self.playlist_panels[playlist].pack(side='top', fill='x', padx=5, pady=(0, 5))
        self.playlist_panel.pack(side='top', fill='both')
        # delete button
        self.delete_button = ttk.Button(self, image=self.icons['delete'], text='Remove', compound='left', command=self.remove_from_playlist)
        self.delete_button.pack(side='top', fill='x', padx=5, pady=(5, 5))

    def show(self, song: str) -> None:
        self.song = song
        self.update_options()
        self.set_position()
        if not self.animation:
            self.deiconify()
            self.animation = self.after(0, self.animate)
        self.focus_set()

    def hide(self) -> None:
        self.withdraw()

    def update_options(self) -> None:
        selected_playlist: str = self.playlist_menu.get()
        # block playlists
        for playlist in self.playlists:
            if playlist != 'Favorites':
                if self.song in self.playlists[playlist]['Songs']:
                    self.playlist_panels[playlist].state(['disabled'])
                    self.disabled_playlists.append(playlist)
                elif playlist in self.disabled_playlists:
                    self.playlist_panels[playlist].state(['!disabled'])
                    self.disabled_playlists.remove(playlist)
        # block buttons
        if selected_playlist == 'Favorites':
            self.delete_button.state(['disabled'])
        else:
            self.delete_button.state(['!disabled'])

    def set_position(self) -> None:
        # get mouse position
        mouse_pos: tuple = self.parent.winfo_pointerxy()
        # get window dimensions
        dimensions: tuple = (self.winfo_width(), self.winfo_height())
        # get button class
        button: ttk.Button = self.parent.winfo_containing(mouse_pos[0], mouse_pos[1])
        if button:
            button_position: tuple = (button.winfo_rootx(), button.winfo_rooty())
            if button_position[0] >= self.winfo_screenwidth() - dimensions[0] - 45:
                self.geometry(f'+{button_position[0] - dimensions[0] - 10}+{button_position[1] - 6}')
            else:
                self.geometry(f'+{button_position[0] + 45}+{button_position[1] - 6}')
        else:
            self.geometry(f'+{mouse_pos[0]}+{mouse_pos[1]}')

    def animate(self) -> None:
        # get window dimensions
        dimensions: tuple = (self.winfo_width(), self.winfo_height())
        num_of_panels: int = len(self.playlists) + 1
        speed: int = 5
        for step in range(int(dimensions[1] / num_of_panels / speed)):
            sleep(.0001)
            self.geometry(f'{dimensions[0]}x{step * num_of_panels * speed}')
            self.update()
        # reset geometry after animation
        self.geometry('')
        # ready
        self.animation = None

    def append(self, playlist: str) -> None:
        self.playlist_panels[playlist] = ttk.Button(self.playlist_panel, image=self.icons['playlist'][0], text=self.playlists[playlist]['Name'], compound='left', command=lambda: self.add_to_playlist(playlist))
        self.playlist_panels[playlist].pack(side='top', fill='x', padx=5, pady=(0, 5))

    def remove(self, playlist: str) -> None:
        if playlist in self.playlist_panels:
            self.playlist_panels[playlist].destroy()
            del self.playlist_panels[playlist]
        if playlist in self.disabled_playlists:
            self.disabled_playlists.remove(playlist)

    def rename(self, playlist: str, name: str) -> None:
        self.playlist_panels[playlist]['text'] = name

    def remove_from_playlist(self) -> None:
        selected_playlist: str = self.playlist_menu.get()
        if selected_playlist == 'Library':
            self.parent.remove_song(self.song)
        elif selected_playlist != 'Favorites' and selected_playlist in self.playlists and self.song in self.playlists[selected_playlist]['Songs']:
            self.playlists[selected_playlist]['Songs'].remove(self.song)
            if self.song in self.parent.songs:
                self.parent.songs.remove(self.song)
            if self.song in self.parent.song_panels:
                self.parent.song_panels[self.song].pack_forget()
            if not self.playlists[selected_playlist]['Songs']:
                self.parent.no_songs.pack(side='top', fill='x', pady=5, padx=10)
        self.hide()

    def add_to_playlist(self, playlist: str) -> None:
        if playlist in self.playlists and self.song in self.parent.library and not self.song in self.playlists[playlist]['Songs']:
            self.playlists[playlist]['Songs'].append(self.song)
        self.hide()

    def add_playlist(self) -> None:
        self.parent.add_playlist()
        self.add_to_playlist(list(self.playlists.keys())[-1])
