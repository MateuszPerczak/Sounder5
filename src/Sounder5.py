try:
    from tkinter import Tk, ttk, StringVar, BooleanVar, DoubleVar, Canvas, Event, IntVar, PhotoImage
    from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfile
    from tkinter.messagebox import askyesno
    from os.path import isfile, join, isdir, basename, abspath, join, splitext, dirname, exists
    from os import startfile, listdir, walk
    from json import load, dump
    from json.decoder import JSONDecodeError
    from logging import basicConfig, error
    from traceback import format_exc
    from PIL import Image, ImageTk
    from io import BytesIO
    from random import choices, shuffle
    from string import ascii_uppercase, digits
    from Components.SystemTheme import get_theme
    from Components.SongMenu import SongMenu
    from Components.DirWatcher import DirWatcher
    from requests import get
    from threading import Thread
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    from difflib import SequenceMatcher
    from pygame import mixer
    from win10toast import ToastNotifier
    from typing import Union
    import ctypes
    from time import sleep
except ImportError as err:
    exit(err)


class Sounder(Tk):
    def __init__(self: Tk) -> None:
        super().__init__()
        # init logging errors
        self.init_logging()
        # hide window
        self.withdraw()
        # configure window
        self.minsize(800, 500)
        self.title('Sounder')
        self.protocol('WM_DELETE_WINDOW', self.exit_app)
        # self.bind('<F12>', lambda _: Debugger(self))
        # self.attributes('-alpha', 0.9)
        # init notifications
        Thread(target=self.init_notifications, daemon=True).start()
        # init settings
        self.init_settings()
        self.apply_settings()
        # init layout
        self.init_layout()
        # load icons
        self.load_icons()
        # init theme
        self.apply_theme()
        # init screen
        self.deiconify()
        self.init_important_panels()
        # self.init_important_panels()
        self.update_idletasks()
        # init ui
        self.init_ui()
        # init player
        self.init_player()
        # show main panel
        self.after(50, lambda: self.player_panel.lift())

    def init_important_panels(self: Tk) -> None:
        try:
            # error panel
            self.error_panel: ttk.Frame = ttk.Frame(self)
            error_content: ttk.Frame = ttk.Frame(self.error_panel)
            ttk.Label(error_content, image=self.icons['error'], text='Something went wrong',
                      compound='top', style='second.TLabel').pack(side='top')
            self.error_label: ttk.Label = ttk.Label(
                error_content, text='We are unable to display the error message!', style='third.TLabel')
            self.error_label.pack(side='top')
            ttk.Button(error_content, text='Exit', style='third.TButton',
                       command=self.exit_app).pack(side='top', pady=(50, 0), padx=10)
            ttk.Button(error_content, text='Ignore', style='third.TButton',
                       command=lambda: self.error_panel.lower()).pack(side='top', pady=(10, 0), padx=10)
            ttk.Button(error_content, text='Open Logs', style='third.TButton',
                       command=self.open_logs).pack(side='top', pady=(10, 0), padx=10)
            ttk.Button(error_content, text='Report an issue', style='third.TButton',
                       command=self.open_logs).pack(side='top', pady=(10, 0), padx=10)
            error_content.place(relx=.5, rely=.5, anchor='center')
            ttk.Label(self.error_panel, text=f'version: {self.version[0]} [build: {self.version[1]}]', style='third.TLabel').pack(
                side='bottom', anchor='w', padx=10, pady=5)
            self.error_panel.place(x=0, y=0, relwidth=1, relheight=1)
            # init panel
            init_panel: ttk.Frame = ttk.Frame(self, style='second.TFrame')
            ttk.Label(init_panel, image=self.icons['logo']).place(
                relx=.5, rely=.5, anchor='center')
            init_panel.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as err_obj:
            self.log(err_obj)

    def init_logging(self: Tk) -> None:
        # logging error messages
        basicConfig(filename=fr'Resources\\Dumps\\sounder_dump.txt', level=40)

    def log(self: Tk, err_obj: object) -> None:
        # DING!!!!!!
        self.bell()
        # log error to file
        error(err_obj, exc_info=True)
        self.error_label['text'] = format_exc().split("\n")[-2]
        self.error_panel.lift()
        # stop playback
        try:
            mixer.music.stop()
        except Exception as _:
            pass

    def init_notifications(self: Tk) -> None:
        self.toaster = ToastNotifier()

    def init_settings(self: Tk) -> None:
        try:
            # variables
            default_settings: dict = {'played_percent': 2, 'menu_position': 'left', 'search_compensation': 0.7, 'delete_missing': False, 'follow': 1, 'crossfade': 100, 'shuffle': False, 'start_playback': False, 'playlist': 'Library', 'repeat': 'None', 'buffer': 'Normal', 'last_song': '',
                                      'volume': 0.5, 'sort_by': 'A-Z', 'scan_subfolders': False, 'geometry': '800x500', 'wheel_acceleration': 1.0, 'updates': True, 'folders': [], 'use_system_theme': True, 'theme': 'Light', 'page': 'Library', 'playlists': {'Favorites': {'Name': 'Favorites', 'Songs': []}}}
            self.settings: dict = {}
            self.version: tuple = ('0.8.2', '150122')
            # load settings
            if isfile(r'Resources\\Settings\\Settings.json'):
                with open(r'Resources\\Settings\\Settings.json', 'r') as data:
                    try:
                        self.settings = load(data)
                    except JSONDecodeError as err_obj:
                        self.settings = default_settings
            else:
                self.settings = default_settings
                # open sounder configurator
                from Components.Setup import SSetup
                SSetup(self, self.settings).mainloop()
            # verify settings
            for key in default_settings:
                self.settings[key] = self.settings.get(
                    key, default_settings[key])
            # verify playlist
            if not 'Favorites' in self.settings['playlists']:
                self.settings['playlists']['Favorites'] = {
                    'Name': 'Favorites', 'Songs': []}
        except Exception as err_obj:
            self.log(err_obj)

    def apply_settings(self: Tk) -> None:
        # check theme
        if self.settings['use_system_theme']:
            self.settings['theme'] = get_theme()
        # check for updates
        if self.settings['updates']:
            self.after(5000, self.update_thread)
        # bind escape to root window
        self.bind('<Escape>', lambda _: self.focus_set())
        # bind scroll to content
        self.bind('<MouseWheel>', self.on_wheel)
        # apply geometry
        self.geometry(self.settings['geometry'])

    def save_settings(self: Tk) -> None:
        # save last page
        active_panel: str = self.menu_option.get()
        if active_panel != 'Updates':
            self.settings['page'] = active_panel
        # save player state ...
        # save app geometry
        self.settings['geometry'] = f'{self.geometry()}'
        # save active playlists
        self.settings['playlist'] = self.playlist
        try:
            with open(r'Resources\\Settings\\Settings.json', 'w') as data:
                dump(self.settings, data)
        except Exception as err_obj:
            self.log(err_obj)

    def restore_default(self: Tk) -> None:
        if askyesno('Restore default configuration', 'Are you sure you want to restore the default configuration?', icon='warning'):
            self.settings = {}
            self.exit_app()

    def init_layout(self: Tk) -> None:
        # init theme object
        self.layout = ttk.Style()
        # set theme to clam
        self.layout.theme_use('clam')
        # button
        self.layout.layout('TButton', [('Button.padding', {
                           'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # radiobutton
        self.layout.layout('TRadiobutton', [('Radiobutton.padding', {
                           'sticky': 'nswe', 'children': [('Radiobutton.label', {'sticky': 'nswe'})]})])
        # scrollbar
        self.layout.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [
                           ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
        # entry
        self.layout.layout('TEntry', [('Entry.padding', {'sticky': 'nswe', 'children': [
                           ('Entry.textarea', {'sticky': 'nswe'})]})])

    def apply_theme(self: Tk) -> None:
        theme: dict = {'Dark': ['#111', '#212121', '#333', '#fff'], 'Light': [
            '#fff', '#ecf0f1', '#ecf0f1', '#000'], 'Contrast': ['#000', '#444', '#444', '#3ff23f']}
        # window
        self.configure(background=theme[self.settings['theme']][1])
        # frame
        self.layout.configure(
            'TFrame', background=theme[self.settings['theme']][1])
        self.layout.configure(
            'second.TFrame', background=theme[self.settings['theme']][0])
        # label
        self.layout.configure('TLabel', background=theme[self.settings['theme']][0], relief='flat', font=(
            'catamaran 12 bold'), foreground=theme[self.settings['theme']][3])
        self.layout.configure(
            'second.TLabel', background=theme[self.settings['theme']][1], font=('catamaran 20 bold'))
        self.layout.configure(
            'third.TLabel', background=theme[self.settings['theme']][1])
        self.layout.configure(
            'fourth.TLabel', background=theme[self.settings['theme']][1], font=('catamaran 16 bold'))
        self.layout.configure(
            'fifth.TLabel', background=theme[self.settings['theme']][0], font=('catamaran 10 bold'))
        self.layout.configure(
            'sixth.TLabel', background=theme[self.settings['theme']][0], font=('catamaran 8 bold'))
        self.layout.configure(
            'seventh.TLabel', background=theme[self.settings['theme']][0], font=('catamaran 16 bold'))
        # radiobuttoncheck_update
        self.layout.configure('TRadiobutton', background=theme[self.settings['theme']][0], relief='flat', font=(
            'catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w', padding=5, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), (
            'active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('second.TRadiobutton',
                              anchor='center', padding=5, width=6)
        self.layout.configure('third.TRadiobutton',
                              anchor='center', padding=5, width=8)
        self.layout.configure('fourth.TRadiobutton', anchor='center')
        self.layout.configure('fifth.TRadiobutton', font=(
            'catamaran 12 bold'), background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3], anchor='center', padding=4, width=6)
        self.layout.map('fifth.TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), (
            'active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        self.layout.configure('sixth.TRadiobutton', font=(
            'catamaran 12 bold'), background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3], anchor='center', padding=4, width=10)
        self.layout.map('sixth.TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), (
            'active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        # button
        self.layout.configure('TButton', background=theme[self.settings['theme']][0], relief='flat', font=(
            'catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w')
        self.layout.map('TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), (
            'active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure(
            'second.TButton', background=theme[self.settings['theme']][1], anchor='center')
        self.layout.map('second.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), (
            'active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        self.layout.configure(
            'third.TButton', background=theme[self.settings['theme']][0], anchor='center')
        self.layout.map('third.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), (
            'active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('fourth.TButton', anchor='center',
                              background=theme[self.settings['theme']][1], width=20)
        self.layout.map('fourth.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), (
            'active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        # scrollbar
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background=theme[self.settings['theme']][1], darkcolor=theme[self.settings['theme']][
                              1], lightcolor=theme[self.settings['theme']][1], troughcolor=theme[self.settings['theme']][1], bordercolor=theme[self.settings['theme']][1])
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), (
            'disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][0]), ('!active', theme[self.settings['theme']][0])])
        # scale
        self.layout.map('Horizontal.TScale', background=[
                        ('pressed', '!disabled', theme[self.settings['theme']][2]), ('active', theme[self.settings['theme']][2])])
        # self.layout.configure('Horizontal.TScale', troughcolor='#151515', background='#333', relief="flat", gripcount=0, darkcolor="#151515", lightcolor="#151515", bordercolor='#151515')
        self.layout.configure('Horizontal.TScale', troughcolor=theme[self.settings['theme']][0], background=theme[self.settings['theme']][1], relief='flat',
                              gripcount=0, darkcolor=theme[self.settings['theme']][0], lightcolor=theme[self.settings['theme']][0], bordercolor=theme[self.settings['theme']][0])
        # entry
        self.layout.configure('TEntry', background=theme[self.settings['theme']][1], insertcolor=theme[self.settings['theme']][3], foreground=theme[self.settings['theme']]
                              [3], fieldbackground=theme[self.settings['theme']][0], selectforeground=theme[self.settings['theme']][3], selectbackground=theme[self.settings['theme']][2])
        self.layout.map('TEntry', foreground=[
                        ('active', '!disabled', 'disabled', theme[self.settings['theme']][3])])
        self.layout.configure(
            'second.TEntry', background=theme[self.settings['theme']][0])
        # progressbar
        self.layout.configure("Horizontal.TProgressbar", background=theme[self.settings['theme']][1], lightcolor=theme[self.settings['theme']][0],
                              darkcolor=theme[self.settings['theme']][0], bordercolor=theme[self.settings['theme']][0], troughcolor=theme[self.settings['theme']][0], thickness=2)

    def load_icons(self: Tk) -> None:
        self.icons: dict = {
            'error': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\error.png'),
            'library': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\library.png'),
            'folder': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\folder.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\music_folder.png')),
            'settings': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\settings.png'),
            'plus': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\plus.png'),
            'heart': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\heart_empty.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\heart_filled.png')),
            'delete': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\delete.png'),
            'playlist': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\playlist.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\lounge.png')),
            'play_pause': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\play.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\pause.png')),
            'next': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\next.png'),
            'previous': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\previous.png'),
            'repeat': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\repeat.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\repeat_one.png')),
            'shuffle': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\shuffle.png'),
            'edit': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\edit.png'),
            'menu': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\menu.png'),
            'date': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\date.png'),
            'note': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\note.png'),
            'arrow': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\left.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\right.png')),
            'checkmark': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\checkmark.png'),
            'restore': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\restore.png'),
            'brush': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\brush.png'),
            'info': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\info.png'),
            'window': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\window.png'),
            'user': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\user.png'),
            'icons8': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\icons8.png'),
            'code': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\code.png'),
            'download': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\download.png'),
            'wheel': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\wheel.png'),
            'search': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\search.png'),
            'filter': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\filter.png'),
            'speaker': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\muted.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\low_volume.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\med_volume.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\max_volume.png')),
            'buffer': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\buffer.png'),
            'select': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\select.png'),
            'power': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\power.png'),
            'time': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\time.png'),
            'sort': (PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\no_sort.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\normal_sort.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\reversed_sort.png'), PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\star.png')),
            'puzzled': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\puzzled.png'),
            'package': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\package.png'),
            'shield': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\shield.png'),
            'trash': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\trash.png'),
            'logo': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\logo.png'),
            'navigation': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\navigation.png'),
            'passed': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\passed_time.png'),
            'bug': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\bug.png'),
            'expand': PhotoImage(file=fr'Resources\\Icons\\{self.settings["theme"]}\\expand.png')
        }
        self.iconbitmap(
            fr'Resources\\Icons\\{self.settings["theme"]}\\icon.ico')

    def init_ui(self: Tk) -> None:
        # ui variables
        self.menu_option: StringVar = StringVar(value=self.settings['page'])
        self.menu_playlist: StringVar = StringVar(value=self.settings['page'])
        self.muted: bool = True if self.settings['volume'] == 0.0 else False
        self.last_panel: str = ''
        self.folder_panels: dict = {}
        self.song_panels: dict = {}
        self.settings_panels: tuple = ()
        self.update_panels: list = []
        # theme
        self.theme: StringVar = StringVar()
        if self.settings['use_system_theme']:
            self.theme.set('System')
        else:
            self.theme.set(self.settings['theme'])
        # update
        self.updates: BooleanVar = BooleanVar(value=self.settings['updates'])
        # wheel acceleration
        self.wheel_acceleration: DoubleVar = DoubleVar(
            value=self.settings['wheel_acceleration'])
        # search compensation
        self.search_compensation: DoubleVar = DoubleVar(
            value=self.settings['search_compensation'])
        # scan subfolders
        self.scan_subfolders: BooleanVar = BooleanVar(
            value=self.settings['scan_subfolders'])
        # sort by
        self.sort_by: StringVar = StringVar(value=self.settings['sort_by'])
        # buffer mode
        self.buffer: StringVar = StringVar(value=self.settings['buffer'])
        # playback
        self.start_playback: BooleanVar = BooleanVar(
            value=self.settings['start_playback'])
        # crossfade
        self.crossfade: DoubleVar = DoubleVar(value=self.settings['crossfade'])
        # follow
        self.follow: IntVar = IntVar(value=self.settings['follow'])
        # missing
        self.delete_missing: BooleanVar = BooleanVar(
            value=self.settings['delete_missing'])
        # menu position
        self.menu_position: StringVar = StringVar(
            value=self.settings['menu_position'])
        # played percent
        self.played_percent: DoubleVar = DoubleVar(
            value=self.settings['played_percent'])
        # songs info
        self.songs_info: StringVar = StringVar(value='')
        # player panel
        self.player_panel: ttk.Frame = ttk.Frame(self)
        # top panel
        player_top_panel: ttk.Frame = ttk.Frame(self.player_panel)
        # menu panel
        self.menu_panel: ttk.Frame = ttk.Frame(
            player_top_panel, style='second.TFrame')
        ttk.Radiobutton(self.menu_panel, image=self.icons['library'], text='Library', compound='left', value='Library',
                        variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=(10, 0))
        ttk.Radiobutton(self.menu_panel, image=self.icons['folder'][1], text='Folders', compound='left', value='Folders',
                        variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=10)
        ttk.Radiobutton(self.menu_panel, image=self.icons['settings'], text='Settings', compound='left', value='Settings',
                        variable=self.menu_option, command=self.show_panel).pack(side='bottom', fill='x', padx=10, pady=(0, 10))
        ttk.Label(self.menu_panel, text='Playlists').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Button(self.menu_panel, image=self.icons['plus'], text='Add playlist', compound='left', command=self.add_playlist).pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Radiobutton(self.menu_panel, image=self.icons['heart'][1], text='Favorites', compound='left', value='Favorites',
                        variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10)
        # add playlist from settings
        for playlist in self.settings['playlists']:
            if playlist == 'Favorites':
                continue
            ttk.Radiobutton(self.menu_panel, image=self.icons['playlist'][0], text=self.settings['playlists'][playlist]['Name'], compound='left', value=playlist,
                            style='menu.TRadiobutton', variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
        self.menu_panel.pack(side=self.settings['menu_position'], fill='both')
        # player scrollbar
        player_content_scroll = ttk.Scrollbar(
            player_top_panel, orient='vertical')
        player_content_scroll.pack(side='right', fill='y')
        # options panel
        player_options_panel: ttk.Frame = ttk.Frame(player_top_panel)
        # update options panel
        self.update_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.update_options, image=self.icons['download'], text='Updates', style='fourth.TLabel', compound='left').pack(
            side='left', anchor='center', padx=(10, 0))
        self.update_options.place(x=0, y=0, relwidth=1, relheight=1)
        # playlist panel
        self.playlist_panel: ttk.Frame = ttk.Frame(player_options_panel)
        # playlist arbitrary name
        self.playlist_an: ttk.Label = ttk.Label(
            self.playlist_panel, text='', style='fourth.TLabel', compound='left')
        self.playlist_an.pack(side='left', anchor='center', padx=(10, 0))
        self.playlist_an.bind('<Double-Button-1>', self.edit_playlist)
        # playlist menu button
        ttk.Button(self.playlist_panel, image=self.icons['menu'], style='second.TButton', command=lambda: self.playlist_options.lift(
        )).pack(side='right', anchor='center', padx=(0, 15))
        ttk.Button(self.playlist_panel, image=self.icons['select'], style='second.TButton', command=self.target_playlist).pack(
            side='right', anchor='center', padx=(0, 5))
        ttk.Button(self.playlist_panel, image=self.icons['filter'], style='second.TButton', command=lambda: self.sort_options.lift(
        )).pack(side='right', anchor='center', padx=(0, 5))
        # playlist info
        ttk.Label(self.playlist_panel, image=self.icons['note'], textvariable=self.songs_info, compound='left', padding=2, anchor='center').pack(
            side='right', anchor='center', padx=(0, 10), ipadx=5)
        self.playlist_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # playlist options
        self.playlist_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.playlist_options, image=self.icons['edit'], style='third.TLabel').pack(
            side='left', anchor='center', padx=(10, 1))
        # playlist entry
        self.playlist_entry = ttk.Entry(
            self.playlist_options, exportselection=False, font=('catamaran 16 bold'))
        self.playlist_entry.pack(side='left', anchor='center')
        self.playlist_entry.bind('<Return>', self.rename_playlist)
        ttk.Button(self.playlist_options, image=self.icons['arrow'][0], style='second.TButton', command=lambda: self.playlist_panel.lift(
        )).pack(side='right', anchor='center', padx=(5, 15))
        self.playlist_remove: ttk.Button = ttk.Button(
            self.playlist_options, image=self.icons['trash'], style='second.TButton', command=self.remove_playlist)
        self.playlist_remove.pack(side='right', anchor='center')
        self.playlist_options.place(x=0, y=0, relwidth=1, relheight=1)
        # folder options
        self.folder_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.folder_options, image=self.icons['folder'][1], text='Folders', style='fourth.TLabel', compound='left').pack(
            side='left', anchor='center', padx=(10, 0))
        ttk.Button(self.folder_options, image=self.icons['plus'], style='second.TButton', command=self.new_folder).pack(
            side='right', anchor='center', padx=(10, 15))
        self.folder_options.place(x=0, y=0, relwidth=1, relheight=1)
        # settings options
        self.settings_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.settings_options, image=self.icons['settings'], text='Settings', style='fourth.TLabel', compound='left').pack(
            side='left', anchor='center', padx=(10, 0))
        ttk.Button(self.settings_options, image=self.icons['restore'], style='second.TButton', command=self.restore_default).pack(
            side='right', anchor='center', padx=(10, 15))
        self.settings_options.place(x=0, y=0, relwidth=1, relheight=1)
        # library options
        self.library_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.library_options, image=self.icons['library'], text='Library', style='fourth.TLabel', compound='left').pack(
            side='left', anchor='center', padx=(10, 0))
        ttk.Button(self.library_options, image=self.icons['filter'], style='second.TButton', command=lambda: self.sort_options.lift(
        )).pack(side='right', anchor='center', padx=(0, 15))
        ttk.Button(self.library_options, image=self.icons['select'], style='second.TButton', command=self.target_playlist).pack(
            side='right', anchor='center', padx=(0, 5))
        # library search bar
        no_songs: ttk.Frame = ttk.Frame(self.library_options)
        self.lib_search: ttk.Button = ttk.Button(
            no_songs, image=self.icons['search'], style='second.TButton', command=self.open_search)
        self.lib_search.pack(side='right', anchor='center')
        self.lib_entry = ttk.Entry(no_songs, exportselection=False, font=(
            'catamaran 15 bold'), width=12, style='second.TEntry')
        self.lib_entry.bind('<Return>', self.search)
        self.lib_entry.bind('<KeyRelease>', self.search)
        no_songs.pack(side='right', anchor='center', padx=(0, 5))
        # library info
        ttk.Label(self.library_options, image=self.icons['note'], textvariable=self.songs_info, compound='left', padding=2, anchor='center').pack(
            side='right', anchor='center', padx=(0, 10), ipadx=5)
        self.library_options.place(x=0, y=0, relwidth=1, relheight=1)
        # sort options
        self.sort_options: ttk.Frame = ttk.Frame(player_options_panel)
        ttk.Label(self.sort_options, image=self.icons['filter'], text='Sort by', style='fourth.TLabel', compound='left').pack(
            side='left', anchor='center', padx=(10, 0))
        ttk.Button(self.sort_options, image=self.icons['arrow'][0], style='second.TButton', command=lambda: self.sort_options.lower(
        )).pack(side='right', anchor='center', padx=(0, 15))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][0], text='None', compound='left', style='fifth.TRadiobutton',
                        value='#', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='center', padx=(0, 10))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][2], text='Name', compound='left', style='fifth.TRadiobutton',
                        value='Z-A', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='center', padx=(0, 5))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][1], text='Name', compound='left', style='fifth.TRadiobutton',
                        value='A-Z', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='center', padx=(0, 5))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][3], text='Most played', compound='left', style='sixth.TRadiobutton',
                        value='NOP', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='center', padx=(0, 5))
        self.sort_options.place(x=0, y=0, relwidth=1, relheight=1)
        player_options_panel.pack(side='top', fill='x', ipady=28.5)
        # player content
        self.player_canvas = Canvas(
            player_top_panel, background=self['background'], bd=0, highlightthickness=0, yscrollcommand=player_content_scroll.set, takefocus=False)
        # link scrollbar to canvas
        player_content_scroll.configure(command=self.player_canvas.yview)
        # player content
        self.player_content: ttk.Frame = ttk.Frame(self.player_canvas)
        self.player_content.bind('<Expose>', lambda _: self.player_canvas.configure(
            scrollregion=self.player_canvas.bbox("all")))
        self.content_window = self.player_canvas.create_window(
            (0, 0), window=self.player_content, anchor='nw')
        self.player_canvas.bind('<Expose>', lambda _: self.player_canvas.itemconfigure(
            self.content_window, width=self.player_canvas.winfo_width(), height=0))
        self.player_canvas.pack(side='top', fill='both', expand=True)
        player_top_panel.pack(side='top', fill='both', expand=True)
        # add folders from settings
        for folder in self.settings['folders']:
            self.add_folder(abspath(folder))
        # settings panels
        # theme
        settings_theme: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        theme_panel: ttk.Frame = ttk.Frame(
            settings_theme, style='second.TFrame')
        ttk.Label(theme_panel, image=self.icons['brush'], text='Theme', style='TLabel', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(theme_panel, text='System', style='second.TRadiobutton', value='System',
                        variable=self.theme, command=self.change_theme).pack(side='right', anchor='center', padx=(0, 10))
        ttk.Radiobutton(theme_panel, text='Light', style='second.TRadiobutton', value='Light',
                        variable=self.theme, command=self.change_theme).pack(side='right', anchor='center', padx=(0, 10))
        ttk.Radiobutton(theme_panel, text='Dark', style='second.TRadiobutton', value='Dark',
                        variable=self.theme, command=self.change_theme).pack(side='right', anchor='center', padx=(0, 10))
        ttk.Radiobutton(theme_panel, text='Contrast', style='third.TRadiobutton', value='Contrast',
                        variable=self.theme, command=self.change_theme).pack(side='right', anchor='center', padx=(0, 10))
        theme_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_theme, image=self.icons['info'], text='Note: You need to restart the application to see any changes!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # acceleration
        settings_acceleration: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(settings_acceleration, image=self.icons['wheel'], text='Wheel acceleration', compound='left').pack(
            side='left', anchor='center', fill='y', pady=10, padx=10)
        ttk.Label(settings_acceleration, text='Fast').pack(
            side='right', anchor='center', fill='y', pady=10, padx=10)
        ttk.Scale(settings_acceleration, variable=self.wheel_acceleration, from_=1, to=8,
                  command=self.change_acceleration).pack(side='right', anchor='center', fill='x', ipadx=40)
        ttk.Label(settings_acceleration, text='Slow').pack(
            side='right', anchor='center', fill='y', pady=10, padx=10)
        # updates
        settings_updates: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(settings_updates, image=self.icons['download'], text='Check for updates', compound='left').pack(
            side='left', anchor='center', fill='y', pady=10, padx=(10, 0))
        ttk.Radiobutton(settings_updates, text='No', style='second.TRadiobutton', value=False, variable=self.updates,
                        command=self.change_updates).pack(side='right', anchor='center', padx=10, pady=10)
        ttk.Radiobutton(settings_updates, text='Yes', style='second.TRadiobutton', value=True,
                        variable=self.updates, command=self.change_updates).pack(side='right', anchor='center', pady=10)
        # about
        settings_about: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(settings_about, image=self.icons['info'], text='About Sounder', compound='left').pack(
            side='top', anchor='center', fill='x', padx=10, pady=10)
        ttk.Label(settings_about, image=self.icons['window'], text=f'Version: {self.version[0]} Build: {self.version[1]}', compound='left').pack(
            side='top', anchor='center', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['user'], text='Author: Mateusz Perczak', compound='left').pack(
            side='top', anchor='center', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['icons8'], text='Icons: Icons8', compound='left').pack(
            side='top', anchor='center', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['code'], text='UI: LUI V2', compound='left').pack(
            side='top', anchor='center', fill='x', padx=10, pady=(0, 10))
        # folders
        settings_subfolders: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        subfolders_panel: ttk.Frame = ttk.Frame(
            settings_subfolders, style='second.TFrame')
        ttk.Label(subfolders_panel, image=self.icons['folder'][0], text='Scan subfolders', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(subfolders_panel, text='No', style='second.TRadiobutton', value=False, variable=self.scan_subfolders,
                        command=self.change_subfolders).pack(side='right', anchor='center', padx=(10, 0))
        ttk.Radiobutton(subfolders_panel, text='Yes', style='second.TRadiobutton', value=True,
                        variable=self.scan_subfolders, command=self.change_subfolders).pack(side='right', anchor='center')
        subfolders_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_subfolders, image=self.icons['info'], text='Note: Scanning subfolders may affect performance!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # mixer buffer
        settings_buffer: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        buffer_panel: ttk.Frame = ttk.Frame(
            settings_buffer, style='second.TFrame')
        ttk.Label(buffer_panel, image=self.icons['buffer'], text='Player buffer mode', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(buffer_panel, text='Fastest', style='third.TRadiobutton', value='Fast',
                        variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='center')
        ttk.Radiobutton(buffer_panel, text='Default', style='third.TRadiobutton', value='Normal',
                        variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='center', padx=10)
        ttk.Radiobutton(buffer_panel, text='Slowest', style='third.TRadiobutton', value='Slow',
                        variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='center')
        buffer_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_buffer, image=self.icons['info'], text='Note: Setting buffet to fastest reduces lag but may increase underturns!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_buffer, image=self.icons['info'], text='Note: You need to restart the application to see any changes!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # startup
        settings_startup: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(settings_startup, image=self.icons['power'], text='On startup', compound='left').pack(
            side='left', anchor='center', fill='y', padx=10)
        ttk.Radiobutton(settings_startup, text='Do nothing', style='fourth.TRadiobutton', value=False,
                        variable=self.start_playback, command=self.change_playback).pack(side='right', anchor='center', padx=(0, 10), pady=10)
        ttk.Radiobutton(settings_startup, text='Start playback', style='fourth.TRadiobutton', value=True,
                        variable=self.start_playback, command=self.change_playback).pack(side='right', anchor='center', padx=(0, 10), pady=10)
        # crossfade
        settings_crossfade: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        crossfade_panel: ttk.Frame = ttk.Frame(
            settings_crossfade, style='second.TFrame')
        ttk.Label(crossfade_panel, image=self.icons['time'], text='Crossfade', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Label(crossfade_panel, text='16s').pack(
            side='right', anchor='center', fill='y', padx=(10, 0))
        ttk.Scale(crossfade_panel, from_=100.0, to=16000.0, variable=self.crossfade,
                  command=self.change_crossfade).pack(side='right', anchor='center', fill='x', ipadx=40)
        ttk.Label(crossfade_panel, text='Off').pack(
            side='right', anchor='center', fill='y', padx=(0, 10))
        crossfade_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_crossfade, image=self.icons['info'], text='Note: Allows you to crossfade between songs!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # follow active song
        settings_active_song: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        active_song_panel: ttk.Frame = ttk.Frame(
            settings_active_song, style='second.TFrame')
        ttk.Label(active_song_panel, image=self.icons['playlist'][1], text='Follow active song', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(active_song_panel, text='Never follow', style='fourth.TRadiobutton', value=0,
                        variable=self.follow, command=self.change_follow).pack(side='right', anchor='center')
        ttk.Radiobutton(active_song_panel, text='Smart follow', style='fourth.TRadiobutton', value=1,
                        variable=self.follow, command=self.change_follow).pack(side='right', anchor='center', padx=10)
        ttk.Radiobutton(active_song_panel, text='Always follow', style='fourth.TRadiobutton', value=2,
                        variable=self.follow, command=self.change_follow).pack(side='right', anchor='center')
        active_song_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_active_song, image=self.icons['info'], text='Note: Sounder will automatically scroll to an active song if found in playlist!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # missing songs
        settings_missing_song: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        missing_song_panel: ttk.Frame = ttk.Frame(
            settings_missing_song, style='second.TFrame')
        ttk.Label(missing_song_panel, image=self.icons['puzzled'], text='Automatically delete missing songs', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(missing_song_panel, text='No', style='second.TRadiobutton', value=False,
                        variable=self.delete_missing, command=self.change_missing).pack(side='right', anchor='center')
        ttk.Radiobutton(missing_song_panel, text='Yes', style='second.TRadiobutton', value=True,
                        variable=self.delete_missing, command=self.change_missing).pack(side='right', anchor='center', padx=10)
        missing_song_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_missing_song, image=self.icons['info'], text='Note: Sounder will delete all missing songs from all playlists!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # export playlists
        settings_export: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(settings_export, image=self.icons['restore'], text='Export/Import settings',
                  compound='left').pack(side='left', anchor='center', fill='y', padx=10)
        ttk.Button(settings_export, text='Export', style='third.TButton', command=self.export_settings).pack(
            side='right', anchor='center', padx=(0, 10), pady=10)
        ttk.Button(settings_export, text='Import', style='third.TButton', command=self.import_settings).pack(
            side='right', anchor='center', padx=(0, 10), pady=10)
        # search tolerance
        settings_tolerance: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        tolerance_panel: ttk.Frame = ttk.Frame(
            settings_tolerance, style='second.TFrame')
        ttk.Label(tolerance_panel, image=self.icons['search'], text='Search spelling compensation', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Label(tolerance_panel, text='Perfection').pack(
            side='right', anchor='center', fill='y', padx=10)
        ttk.Scale(tolerance_panel, from_=0.1, to=1, variable=self.search_compensation,
                  command=self.change_compensation).pack(side='right', anchor='center', fill='x', ipadx=40)
        ttk.Label(tolerance_panel, text='Ignore all').pack(
            side='right', anchor='center', fill='y', padx=10)
        tolerance_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_tolerance, image=self.icons['info'], text='Note: Sounder will ignore all spelling mistakes if set to lowest (not recomended)!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # menu positions
        settings_menu: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        menu_panel: ttk.Frame = ttk.Frame(settings_menu, style='second.TFrame')
        ttk.Label(menu_panel, image=self.icons['navigation'], text='Menu position', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Radiobutton(menu_panel, text='Right', style='second.TRadiobutton', value='right',
                        variable=self.menu_position, command=self.change_menu).pack(side='right', anchor='center', padx=(0, 10))
        ttk.Radiobutton(menu_panel, text='Left', style='second.TRadiobutton', value='left',
                        variable=self.menu_position, command=self.change_menu).pack(side='right', anchor='center', padx=(0, 10))
        menu_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_menu, image=self.icons['info'], text='Note: To see any changes restart is required!', compound='left').pack(
            side='top', fill='x', padx=10, pady=(0, 10))
        # register song as played
        settings_played: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        played_panel: ttk.Frame = ttk.Frame(
            settings_played, style='second.TFrame')
        ttk.Label(played_panel, image=self.icons['passed'], text='Played song sensitivity', compound='left').pack(
            side='left', anchor='center', fill='y')
        ttk.Label(played_panel, text='100%').pack(
            side='right', anchor='center', fill='y', padx=10)
        ttk.Scale(played_panel, from_=2, to=1, variable=self.played_percent,
                  command=self.change_played).pack(side='right', anchor='center', fill='x', ipadx=40)
        ttk.Label(played_panel, text='50%').pack(
            side='right', anchor='center', fill='y', padx=10)
        played_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_played, image=self.icons['info'], text='Note: Sounder will mark a song as played when the passed time is above the set value!', compound='left', wraplength=(
            self.winfo_width() - 250)).pack(side='top', fill='x', padx=10, pady=(0, 10))
        # panels variable
        self.settings_panels = (ttk.Label(self.player_content, text=' User interface', style='third.TLabel'), settings_acceleration, settings_theme, settings_menu, ttk.Label(self.player_content, text=' Playback', style='third.TLabel'), settings_startup, settings_crossfade, settings_buffer, ttk.Label(self.player_content, text=' Songs', style='third.TLabel'), settings_active_song,
                                settings_played, settings_missing_song, ttk.Label(self.player_content, text=' Search', style='third.TLabel'), settings_tolerance, ttk.Label(self.player_content, text=' Folders', style='third.TLabel'), settings_subfolders, ttk.Label(self.player_content, text=' Other', style='third.TLabel'), settings_updates, settings_export, settings_about)
        # bottom panel
        player_bot_panel: ttk.Frame = ttk.Frame(
            self.player_panel, style='second.TFrame')
        # buttons, song name, etc ...
        center_panel: ttk.Frame = ttk.Frame(
            player_bot_panel, style='second.TFrame')
        self.play_button: ttk.Button = ttk.Button(
            center_panel, image=self.icons['play_pause'][0], takefocus=False, command=self.button_play)
        self.play_button.place(relx=0.5, rely=0.5, anchor='center')
        # next button
        ttk.Button(center_panel, image=self.icons['next'], takefocus=False, command=self.button_next).place(
            relx=0.65, rely=0.5, anchor='center')
        # previous button
        ttk.Button(center_panel, image=self.icons['previous'], takefocus=False, command=self.button_previous).place(
            relx=0.35, rely=0.5, anchor='center')
        # shuffle button
        self.shuffle_button: ttk.Button = ttk.Button(
            center_panel, image=self.icons['shuffle'], takefocus=False, command=self.toggle_shuffle)
        self.shuffle_button.place(relx=0.15, rely=0.5, anchor='center')
        if self.settings['shuffle']:
            self.shuffle_button.configure(style='second.TButton')
        else:
            self.shuffle_button.configure(style='TButton')
        # repeat button
        self.repeat_button: ttk.Button = ttk.Button(
            center_panel, takefocus=False, command=self.toggle_repeat)
        if self.settings['repeat'] == 'None':
            self.repeat_button.configure(image=self.icons['repeat'][0])
        elif self.settings['repeat'] == 'All':
            self.repeat_button.configure(
                image=self.icons['repeat'][0], style='second.TButton')
        else:
            self.repeat_button.configure(
                image=self.icons['repeat'][1], style='second.TButton')
        self.repeat_button.place(relx=0.85, rely=0.5, anchor='center')
        center_panel.place(relx=0.5, y=10, width=350, height=48, anchor='n')
        volume_panel: ttk.Frame = ttk.Frame(
            player_bot_panel, style='second.TFrame')
        # mute button
        self.mute_button: ttk.Button = ttk.Button(
            volume_panel, image=self.icons['speaker'][0], takefocus=False, command=self.toggle_volume)
        self.mute_button.pack(side='left', anchor='center', padx=5)
        # volume bar
        self.volume_bar: ttk.Scale = ttk.Scale(
            volume_panel, orient='horizontal', from_=0, to=1, command=self.set_volume)
        self.volume_bar.pack(side='left', anchor='center',
                             padx=5, fill='x', expand=True)
        volume_panel.place(relx=1, y=10, relwidth=0.22, height=48, anchor='ne')
        player_bot_panel.pack(side='top', fill='x', ipady=45)
        self.player_panel.place(x=0, y=0, relwidth=1, relheight=1)
        self.player_panel.lower()
        # left frame
        info_panel: ttk.Frame = ttk.Frame(
            player_bot_panel, style='second.TFrame')
        self.song_album: ttk.Label = ttk.Label(info_panel)
        self.song_album.pack(side='left', padx=10, anchor='center')
        self.favorite_button: ttk.Button = ttk.Button(
            info_panel, image=self.icons['heart'][0],  command=lambda: self.favorites_song(self.song))
        self.favorite_button.pack(side='right', padx=(5, 0), anchor='center')
        info_frame: ttk.Frame = ttk.Frame(info_panel, style='second.TFrame')
        self.song_title: ttk.Label = ttk.Label(
            info_frame, text='', style='fifth.TLabel')
        self.song_title.place(x=0, y=4)
        self.song_artist: ttk.Label = ttk.Label(
            info_frame, text='', style='sixth.TLabel')
        self.song_artist.place(x=0, y=24)
        info_frame.pack(side='left', fill='both', expand=True)
        info_panel.place(relx=0, y=10, relwidth=0.22, height=48, anchor='nw')
        # bottom frame
        progress_frame: ttk.Frame = ttk.Frame(
            player_bot_panel, style='second.TFrame')
        # time passed
        self.time_passed: ttk.Label = ttk.Label(
            progress_frame, text='--:--', anchor='center', justify='center', style='sixth.TLabel')
        self.time_passed.pack(side='left', ipadx=10)
        # progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side='left', fill='x', expand=True)
        self.progress_bar.bind('<Button-1>', self.progress_play)
        # song length
        self.song_length: ttk.Label = ttk.Label(
            progress_frame, text='--:--', anchor='center', justify='center', style='sixth.TLabel')
        self.song_length.pack(side='right', ipadx=10)
        progress_frame.place(relx=0.5, y=68, relwidth=1, height=20, anchor='n')
        # info panels
        self.no_songs: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(self.no_songs, image=self.icons['info'], text='No songs found!', compound='left').pack(
            side='left', anchor='center', fill='y', pady=10, padx=10)

    def init_player(self: Tk) -> None:
        # variables
        self.library: list = []
        self.songs_cache: dict = {}
        self.active_panels: list = []
        self.paused: bool = False
        self.playlist: str = self.settings['playlist']
        self.songs: list = []
        self.after_job: Union[str, None] = None
        self.songs_queue: list = []
        self.offset: float = 0
        # set last song
        self.song: str = self.settings['last_song']
        # init mixer
        # self.init_mixer()
        Thread(target=self.init_mixer, daemon=True).start()
        # scan folders
        self.scan_folders()
        # verify playlists
        Thread(target=self.verify_playlist, daemon=True).start()
        # show last panel
        self.show_panel() if self.settings['page'] in (
            'Library', 'Folders', 'Settings') else self.show_playlist()
        # load last song info
        self.update_info_panel(self.song)
        # restore volume
        self.volume_bar.set(self.settings['volume'])
        # song menu
        self.song_menu = SongMenu(self)
        # mixer thread
        self.mixer_active: bool = False
        if self.settings['start_playback']:
            self.after(10, self.button_play)
        # dir watcher
        Thread(target=self.init_watcher, daemon=True).start()
        # self.init_watcher()

    def on_song_delete(self: Tk, song: str) -> None:
        try:
            if song in self.library:
                self.remove_song(song)
                visible_playlist: str = self.menu_playlist.get()
                for playlist in self.settings['playlists']:
                    if song in self.settings['playlists'][playlist]['Songs']:
                        if self.settings['delete_missing']:
                            self.settings['playlists'][playlist]['Songs'].remove(
                                song)
                        else:
                            self.add_missing_song(song)
                    if playlist == visible_playlist:
                        self.song_panels[song].pack(
                            side='top', fill='x', pady=5, padx=10)
        except Exception as err_obj:
            self.log(err_obj)

    def on_song_add(self: Tk, song: str) -> None:
        sleep(2)
        if not song in self.library:
            self.library.append(song)
            self.new_song(song)
            # show added song
            visible_playlist: str = self.menu_playlist.get()
            if visible_playlist == 'Library':
                self.song_panels[song].pack(
                    side='top', fill='x', pady=5, padx=10)

    def init_watcher(self: Tk) -> None:
        DirWatcher.on_delete = self.on_song_delete
        DirWatcher.on_add = self.on_song_add
        for priority, folder in enumerate(self.settings['folders']):
            Thread(target=DirWatcher, args=(
                folder, priority + 2,), daemon=True).start()

    def exit_app(self: Tk) -> None:
        self.withdraw()
        self.save_settings()
        self.destroy()

    def show_panel(self: Tk) -> None:
        try:
            target_panel: str = self.menu_option.get()
            self.menu_playlist.set(target_panel)
            if target_panel == 'Library':
                self.library_options.lift()
            elif target_panel == 'Folders':
                self.folder_options.lift()
            elif target_panel == 'Settings':
                self.settings_options.lift()
            elif target_panel == 'Updates':
                self.update_options.lift()
            self.show_panels(target_panel)
        except Exception as err_obj:
            self.log(err_obj)

    def show_panels(self: Tk, panel: str) -> None:
        try:
            if self.last_panel != panel:
                # move content to the top
                self.player_canvas.yview_moveto(0)
                # forget
                if self.last_panel == 'Folders':
                    for folder in self.folder_panels:
                        if self.folder_panels[folder].winfo_ismapped():
                            self.folder_panels[folder].pack_forget()
                if self.last_panel == 'Settings':
                    for setting in self.settings_panels:
                        if setting.winfo_ismapped():
                            setting.pack_forget()
                if self.last_panel == 'Library' or self.last_panel in self.settings['playlists']:
                    for song in self.song_panels:
                        if self.song_panels[song].winfo_ismapped():
                            self.song_panels[song].pack_forget()
                    if self.no_songs.winfo_ismapped():
                        self.no_songs.pack_forget()
                if self.last_panel == 'Updates':
                    for update in self.update_panels:
                        if update.winfo_ismapped():
                            update.pack_forget()
                # pack
                if panel == 'Folders':
                    for folder in self.folder_panels:
                        if not self.folder_panels[folder].winfo_ismapped():
                            self.folder_panels[folder].pack(
                                side='top', fill='x', pady=5, padx=10)
                if panel == 'Settings':
                    for setting in self.settings_panels:
                        if not setting.winfo_ismapped():
                            setting.pack(side='top', fill='x', pady=5, padx=10)
                if panel == 'Library':
                    self.sort_panels('', self.library)
                if panel in self.settings['playlists']:
                    self.sort_panels(
                        '', self.settings['playlists'][panel]['Songs'])
                if panel == 'Updates':
                    for update in self.update_panels:
                        if not update.winfo_ismapped():
                            update.pack(side='top', fill='x', pady=5, padx=10)
            self.last_panel = panel
        except Exception as err_obj:
            self.log(err_obj)

    def open_logs(self: Tk) -> None:
        if isfile(r'Resources\\Dumps\\sounder_dump.txt'):
            startfile(r'Resources\\Dumps\\sounder_dump.txt')
            self.exit_app()

    def on_wheel(self: Tk, event: Event) -> None:
        self.player_canvas.yview_scroll(
            int(-self.settings['wheel_acceleration']*(event.delta/120)), 'units')

    def show_playlist(self: Tk) -> None:
        try:
            selected_playlist: str = self.menu_playlist.get()
            self.menu_option.set(selected_playlist)
            self.update_playlist(selected_playlist)
            # show playlist name
            self.playlist_panel.lift()
            self.show_panels(selected_playlist)
            del selected_playlist
        except Exception as err_obj:
            self.log(err_obj)

    def update_playlist(self: Tk, selected_playlist: str) -> None:
        try:
            if selected_playlist in self.settings['playlists']:
                # update playlist info
                self.playlist_an['text'] = self.settings['playlists'][selected_playlist]['Name']
                # update entry
                self.playlist_entry.state(['!disabled'])
                self.playlist_entry.delete(0, 'end')
                self.playlist_entry.insert(
                    0, self.settings['playlists'][selected_playlist]['Name'])
                # change icon acording to playlist type and disable some buttons
                if selected_playlist == 'Favorites':
                    self.playlist_an['image'] = self.icons['heart'][1]
                    # disable button
                    self.playlist_remove.state(['disabled'])
                    # disable entry
                    self.playlist_entry.state(['disabled'])
                    self.playlist_entry.configure(cursor='no')
                else:
                    self.playlist_an['image'] = self.icons['playlist'][0]
                    self.playlist_entry.configure(cursor='ibeam')
                    # enable button
                    self.playlist_remove.state(['!disabled'])
        except Exception as err_obj:
            self.log(err_obj)

    def add_playlist(self: Tk) -> None:
        try:
            playlist_id: str = ''.join(choices(ascii_uppercase + digits, k=4))
            if not playlist_id in self.settings['playlists']:
                self.settings['playlists'][playlist_id] = {
                    'Name': f'Playlist {len(self.settings["playlists"])}', 'Songs': []}
                ttk.Radiobutton(self.menu_panel, image=self.icons['playlist'][0], text=self.settings['playlists'][playlist_id]['Name'], compound='left',
                                value=playlist_id, variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
                self.song_menu.append(playlist_id)
        except Exception as err_obj:
            self.log(err_obj)

    def remove_playlist(self: Tk):
        try:
            if askyesno('Remove playlist', 'Are you sure you want to remove this playlist?\nThis cannot be undone!', icon='warning'):
                selected_playlist: str = self.menu_playlist.get()
                playlist_list: list = list(self.settings['playlists'].keys())
                if selected_playlist in self.settings['playlists'] and selected_playlist != 'Favorites':
                    playlist_list.remove(selected_playlist)
                    # selects last playlist
                    self.menu_playlist.set(
                        playlist_list[len(playlist_list) - 1])
                    self.show_playlist()
                    # update active playlist
                    if selected_playlist == self.playlist:
                        self.playlist = playlist_list[len(playlist_list) - 1]
                    # removes playlist button
                    self.get_playlist_button(selected_playlist).destroy()
                    self.song_menu.remove(selected_playlist)
                    del self.settings['playlists'][selected_playlist]
        except Exception as err_obj:
            self.log(err_obj)

    def get_playlist_button(self: Tk, playlist: str) -> Union[ttk.Radiobutton, None]:
        try:
            return list(filter(lambda widget: widget.winfo_class() == 'TRadiobutton' and widget['text'] == self.settings['playlists'][playlist]['Name'], self.menu_panel.winfo_children()))[0]
        except Exception as err_obj:
            self.log(err_obj)

    def rename_playlist(self: Tk, _) -> None:
        try:
            selected_playlist: str = self.menu_playlist.get()
            new_name: str = self.playlist_entry.get()
            if selected_playlist in self.settings['playlists'] and selected_playlist != 'Favorites' and new_name.strip():
                self.get_playlist_button(selected_playlist)[
                    'text'] = new_name[:14]
                self.settings['playlists'][selected_playlist]['Name'] = new_name[:14]
                self.song_menu.rename(selected_playlist, new_name[:14])
                self.playlist_panel.lift()
            self.update_playlist(selected_playlist)
        except Exception as err_obj:
            self.log(err_obj)

    def verify_playlist(self: Tk) -> None:
        try:
            for playlist in self.settings['playlists']:
                for song in self.settings['playlists'][playlist]['Songs']:
                    if not song in self.library:
                        if self.settings['delete_missing']:
                            self.settings['playlists'][playlist]['Songs'].remove(
                                song)
                        else:
                            if song not in self.song_panels:
                                self.add_missing_song(song)
        except Exception as err_obj:
            self.log(err_obj)

    def add_missing_song(self: Tk, song: str) -> None:
        try:
            self.song_panels[song] = ttk.Frame(
                self.player_content, style='second.TFrame')
            ttk.Label(self.song_panels[song], image=self.icons['puzzled']).pack(
                side='left', anchor='center', pady=10, padx=10)
            info_frame: ttk.Frame = ttk.Frame(
                self.song_panels[song], style='second.TFrame')
            ttk.Label(info_frame, text=basename(song),
                      style='fifth.TLabel').place(x=5, y=5)
            ttk.Label(info_frame, text='Missing',
                      style='sixth.TLabel').place(x=5, y=28)
            info_frame.pack(side='left', fill='both', expand=True)
            ttk.Button(self.song_panels[song], image=self.icons['delete'], command=lambda: self.remove_missing_song(
                song)).pack(side='right', anchor='center', fill='y', pady=10, padx=(0, 5))
        except Exception as err_obj:
            self.log(err_obj)

    def remove_missing_song(self: Tk, song: str) -> None:
        try:
            playlist = self.menu_playlist.get()
            self.settings['playlists'][playlist]['Songs'].remove(song)
            self.song_panels[song].pack_forget()
            if not self.settings['playlists'][playlist]['Songs']:
                self.no_songs.pack(side='top', fill='x', pady=5, padx=10)
        except Exception as err_obj:
            self.log(err_obj)

    def new_folder(self: Tk) -> None:
        try:
            new_dir: str = askdirectory()
            if new_dir and abspath(new_dir) not in self.settings['folders']:
                new_dir = abspath(new_dir)
                self.settings['folders'].append(new_dir)
                self.add_folder(new_dir)
                self.folder_panels[new_dir].pack(
                    side='top', fill='both', expand=True, pady=5, padx=10)
                Thread(target=self.scan_folders, daemon=True).start()
                Thread(target=DirWatcher, args=(
                    new_dir, 1,), daemon=True).start()
        except Exception as err_obj:
            self.log(err_obj)

    def add_folder(self: Tk, path: str) -> None:
        try:
            self.folder_panels[path] = ttk.Frame(
                self.player_content, style='second.TFrame')
            path_label: ttk.Label = ttk.Label(
                self.folder_panels[path], image=self.icons['folder'][0], text=basename(path), compound='left')
            path_label.pack(side='left', anchor='center',
                            fill='y', pady=10, padx=10)
            ttk.Button(self.folder_panels[path], image=self.icons['delete'], takefocus=False,
                       command=lambda: self.remove_folder(path)).pack(side='right', padx=10, anchor='center')
            self.folder_panels[path].bind(
                '<Leave>', lambda _: path_label.configure(text=basename(path)))
            self.folder_panels[path].bind(
                '<Enter>', lambda _: path_label.configure(text=path))
        except Exception as err_obj:
            self.log(err_obj)

    def remove_folder(self: Tk, path: str) -> None:
        try:
            if askyesno('Remove folder', 'Are you sure you want to remove this folder?', icon='warning') and path in self.settings['folders']:
                self.folder_panels[path].destroy()
                self.settings['folders'].remove(path)
                self.remove_songs(path)
                del self.folder_panels[path]
        except Exception as err_obj:
            self.log(err_obj)

    def remove_songs(self: Tk, path: str) -> None:
        try:
            path = abspath(path)
            temp_songs: list = self.library.copy()
            if self.song in temp_songs and path == dirname(self.song):
                self.song = ''
                self.refresh_ui()
                if mixer.music.get_busy():
                    mixer.music.stop()
                    mixer.music.unload()
            if self.settings['scan_subfolders']:
                # get subdirectories
                folders: list = [path, ]
                for folder in walk(path):
                    if not folder[0] in self.settings['folders'] and not folder[0] in folders:
                        folders.append(folder[0])
                for song in temp_songs:
                    if dirname(song) in folders:
                        self.remove_song(song)
            else:
                for song in temp_songs:
                    if path == dirname(song):
                        self.remove_song(song)
        except Exception as err_obj:
            self.log(err_obj)

    def refresh_ui(self: Tk) -> None:
        self.update_info_panel('')
        self.time_passed['text'] = '0:00'
        self.song_length['text'] = '0:00'
        self.progress_bar.configure(value=0, maximum=100)

    def scan_folders(self: Tk) -> None:
        try:
            if self.settings['scan_subfolders']:
                folders: list = self.settings['folders'].copy()
                for folder in folders:
                    if exists(folder):
                        for file in listdir(folder):
                            if file.endswith(('.mp3', '.flac', '.ogg')) and file not in self.library:
                                self.library.append(
                                    abspath(join(folder, file)))
                            elif isdir(join(folder, file)) and file not in ('System Volume Information', '$RECYCLE.BIN') and file not in folders:
                                folders.append(abspath(join(folder, file)))
            else:
                for folder in self.settings['folders']:
                    if exists(folder):
                        for file in listdir(folder):
                            if file.endswith(('.mp3', '.flac', '.ogg')) and file not in self.library:
                                self.library.append(
                                    abspath(join(folder, file)))
            # add songs to cache
            for song in filter(lambda song: not song in self.songs_cache, self.library):
                self.new_song(song)
            # for song in self.library:
            #     if not song in self.songs_cache:
            #         self.new_song(song)
            # add songs to list
            if self.playlist in self.settings['playlists']:
                self.songs = self.library.copy(
                ) if self.playlist == 'Library' else self.settings['playlists'][self.playlist]['Songs']
        except Exception as err_obj:
            self.log(err_obj)

    def change_theme(self: Tk) -> None:
        try:
            theme: str = self.theme.get()
            if theme == 'System':
                self.settings['use_system_theme'] = True
            else:
                self.settings['use_system_theme'] = False
                self.settings['theme'] = theme
        except Exception as err_obj:
            self.log(err_obj)

    def change_updates(self: Tk) -> None:
        self.settings['updates'] = self.updates.get()

    def change_acceleration(self: Tk, _: Event) -> None:
        self.settings['wheel_acceleration'] = round(
            self.wheel_acceleration.get(), 0)

    def change_subfolders(self: Tk) -> None:
        self.settings['scan_subfolders'] = self.scan_subfolders.get()
        Thread(target=self.scan_folders, daemon=True).start()

    def change_buffer(self: Tk) -> None:
        self.settings['buffer'] = self.buffer.get()

    def check_update(self: Tk) -> None:
        try:
            server_version: str = get(
                'https://raw.githubusercontent.com/losek1/Sounder5/master/updates/version.txt').text.strip()
            if server_version != self.version[0] and int(server_version.replace('.', '')) > int(self.version[0].replace('.', '')):
                self.prepare_update_panel(server_version)
                # show notification
                self.toaster.show_toast(f'Update {server_version} is available', 'If you don\'t want to see this message go to settings and disable automatic updates!',
                                        threaded=True, icon_path=r'Resources\\Icons\\Updater\\setup.ico', duration=0)
        except Exception:
            pass

    def update_panel(self: Tk, package_size: str, package_version: str, package_details: str, updates_history: dict) -> None:
        # update panel
        update_panel: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        # update title
        update_title: ttk.Frame = ttk.Frame(
            update_panel, style='second.TFrame')
        ttk.Label(update_title, image=self.icons['package'], text=f'Update version {package_version}', compound='left').pack(
            side='left', padx=10, pady=10)
        ttk.Label(update_title, text=f'{package_size}MB').pack(
            side='right', padx=10, pady=10)
        # pack package title
        update_title.pack(side='top', fill='x')
        # package details
        update_details: ttk.Frame = ttk.Frame(
            update_panel, style='second.TFrame')
        ttk.Label(update_details, text=f'{package_details}', style='fifth.TLabel').pack(
            side='top', fill='x', expand=True)
        # pack package details
        update_details.pack(side='top', fill='x', padx=10, pady=(0, 10))
        # package buttons
        buttons_panel: ttk.Frame = ttk.Frame(
            self.player_content, style='second.TFrame')
        ttk.Label(buttons_panel, image=self.icons['info'], text='Note: This update does not remove any personal data!', compound='left').pack(
            side='left', padx=10)
        ttk.Button(buttons_panel, image=self.icons['checkmark'], text='Update now',
                   compound='left', command=self.do_update).pack(side='right', padx=(0, 10), pady=10)
        # add panels to render
        self.update_panels.append(update_panel)
        self.update_panels.append(buttons_panel)
        # add update button to menu panel
        ttk.Radiobutton(self.menu_panel, image=self.icons['download'], text='Updates', compound='left', value='Updates',
                        variable=self.menu_option, command=self.show_panel).pack(side='bottom', fill='x', padx=10, pady=(0, 10))
        # updates history
        self.update_panels.append(
            ttk.Label(self.player_content, text=' Update history', style='third.TLabel'))
        updates_history['Updates'].reverse()
        for update in updates_history['Updates']:
            history_panel: ttk.Frame = ttk.Frame(
                self.player_content, style='second.TFrame')
            package_panel: ttk.Frame = ttk.Frame(
                history_panel, style='second.TFrame')
            ttk.Label(package_panel, image=self.icons['package'],
                      text=f'Package {update["Version"]}', compound='left').pack(side='left')
            ttk.Label(package_panel, image=self.icons['checkmark'], text='Applied ', compound='right').pack(
                side='right', padx=(10, 0))
            ttk.Label(package_panel, image=self.icons['date'], text=f'{update["Date"]}', compound='right').pack(
                side='right', padx=(0, 10))
            package_panel.pack(fill='x', expand=True, padx=10, pady=(10, 0))
            ttk.Label(history_panel, image=self.icons['shield'], text=f'{update["Hash"]}', compound='left').pack(
                side='top', pady=10, padx=10, fill='x')
            self.update_panels.append(history_panel)

    def prepare_update_panel(self: Tk, package_version: str) -> None:
        # variables
        default_updates: dict = {'Updates': []}
        try:
            package_size: str = f'{round(float(float(int(get("https://raw.githubusercontent.com/losek1/Sounder5/master/updates/package.zip", stream=True).headers.get("Content-Length")) / 1024) / 1024), 1)}'
        except Exception as err_obj:
            package_size: str = '0'
        try:
            package_details: str = get(
                'https://raw.githubusercontent.com/losek1/Sounder5/master/updates/changelog.txt').text
        except Exception as _:
            package_details: str = 'Cannot load update details!'
        # init update history
        if isfile(r'Resources\\Settings\\Updates.json'):
            with open(r'Resources\\Settings\\Updates.json', 'r') as data:
                try:
                    updates_history: dict = load(data)
                except JSONDecodeError as err_obj:
                    updates_history = default_updates
                    with open(r'Resources\\Settings\\Updates.json', 'w') as data:
                        try:
                            dump(updates_history, data)
                        except Exception as err_obj:
                            self.log(err_obj)
        else:
            with open(r'Resources\\Settings\\Updates.json', 'w') as data:
                try:
                    dump(default_updates, data)
                except Exception as err_obj:
                    self.log(err_obj)
            updates_history = default_updates
        # add package panel
        self.update_panel(package_size, package_version,
                          package_details, updates_history)
        # show update
        self.menu_option.set('Updates')
        self.show_panel()

    def do_update(self: Tk) -> None:
        try:
            if isfile('Updater.exe'):
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", 'Updater.exe', self.version[0], None, 1)
        except Exception as err_obj:
            self.log(err_obj)

    def change_playback(self: Tk) -> None:
        self.settings['start_playback'] = self.start_playback.get()

    def change_sort(self: Tk) -> None:
        try:
            sort_by: str = self.sort_by.get()
            if sort_by != self.settings['sort_by']:
                self.settings['sort_by'] = sort_by
                selected_playlist: str = self.menu_option.get()
                if selected_playlist == 'Library':
                    Thread(target=self.sort_panels, args=(
                        self.get_filtered_search(), self.library, True,), daemon=True).start()
                    # self.sort_panels(self.get_filtered_search(), self.library, True)
                elif selected_playlist in self.settings['playlists']:
                    Thread(target=self.sort_panels, args=(
                        '', self.settings['playlists'][selected_playlist]['Songs'], True,), daemon=True).start()
                    # self.sort_panels('', self.settings['playlists'][selected_playlist]['Songs'], True)
        except Exception as err_obj:
            self.log(err_obj)

    def change_crossfade(self: Tk, _: Event) -> None:
        self.settings['crossfade'] = int(self.crossfade.get())

    def change_follow(self: Tk) -> None:
        self.settings['follow'] = self.follow.get()

    def change_missing(self: Tk) -> None:
        self.settings['delete_missing'] = self.delete_missing.get()

    def change_menu(self: Tk) -> None:
        self.settings['menu_position'] = self.menu_position.get()

    def change_played(self: Tk, _: Event) -> None:
        self.settings['played_percent'] = self.played_percent.get()

    def change_compensation(self: Tk, _: Event) -> None:
        self.settings['search_compensation'] = round(
            self.search_compensation.get(), 1)

    def update_thread(self: Tk) -> None:
        Thread(target=self.check_update, daemon=True).start()

    def open_search(self: Tk) -> None:
        entry_content: str = self.lib_entry.get()
        if entry_content:
            self.search()
        else:
            if self.lib_entry.winfo_ismapped():
                self.lib_entry.pack_forget()
                self.lib_search.config(style='second.TButton')
                self.focus_set()
            else:
                self.lib_entry.pack(side='right', anchor='center')
                self.lib_search.config(style='third.TButton')
                self.lib_entry.focus_set()

    def get_filtered_search(self: Tk) -> str:
        allowed_chars: str = 'abcdefghijklmnopqrstuvwxyz123456789. '
        entry_content: str = self.lib_entry.get().lower().strip()
        clean_content: str = ''
        for letter in filter(lambda letter: letter in allowed_chars,
                             entry_content): clean_content += letter
        # for letter in entry_content:
        #     if letter in allowed_chars: clean_content += letter
        return clean_content

    def search(self: Tk, _: Event = None) -> None:
        self.sort_panels(self.get_filtered_search(), self.library, True)
        self.player_canvas.yview_moveto(0)

    def sort_panels(self: Tk, search_word: str, songs: list, refresh_panels: bool = False) -> None:
        try:
            temp_songs: list = []
            # apply search
            if search_word:
                search_word_length: int = len(search_word)
                for song in songs:
                    for token in self.songs_cache[song]['search_tokens']:
                        if song in temp_songs:
                            continue
                        if SequenceMatcher(a=token, b=search_word).quick_ratio() >= self.settings['search_compensation']:
                            temp_songs.append(song)
                        elif search_word == token[:search_word_length]:
                            temp_songs.append(song)
            else:
                temp_songs = songs.copy()
            # apply sort
            if self.settings['sort_by'] == 'A-Z':
                temp_songs.sort(key=self.sort_songs)
            elif self.settings['sort_by'] == 'Z-A':
                temp_songs.sort(key=self.sort_songs, reverse=True)
            elif self.settings['sort_by'] == 'NOP':
                temp_songs.sort(key=self.sort_by_plays, reverse=True)
            if not temp_songs:
                self.no_songs.pack(side='top', fill='x', pady=5, padx=10)
            else:
                self.no_songs.pack_forget()
            # apply search
            if self.playlist == 'Library':
                self.songs = temp_songs.copy()
            # apply shuffle
            if self.songs and self.settings['shuffle']:
                shuffle(self.songs)
            # forget panels
            if refresh_panels:
                for song in filter(lambda song: song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped(), self.library):
                    self.song_panels[song].pack_forget()
                # for song in self.library:
                #     if song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped():
                #         self.song_panels[song].pack_forget()
            else:
                for song in filter(lambda song: song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped(), list(set(temp_songs) ^ set(songs))):
                    self.song_panels[song].pack_forget()
                # for song in list(set(temp_songs)^set(songs)):
                #     if song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped():
                #         self.song_panels[song].pack_forget()
            # pack panels
            for song in filter(lambda song: song in self.song_panels and self.song_panels[song] and not self.song_panels[song].winfo_ismapped(), temp_songs):
                self.song_panels[song].pack(
                    side='top', fill='x', pady=5, padx=10)
            # for song in temp_songs:
            #     if song in self.song_panels and self.song_panels[song] and not self.song_panels[song].winfo_ismapped():
            #         self.song_panels[song].pack(side='top', fill='x', pady=5, padx=10)
            if self.settings['follow'] and not search_word:
                self.show_song(temp_songs)
            # update panel info
            self.songs_info.set(
                f'{len(temp_songs)} {"Songs" if len(temp_songs) > 1 else "Song"}')
        except Exception as err_obj:
            self.log(err_obj)

    def sort_by_plays(self: Tk, song: str) -> int:
        return self.songs_cache[song]['plays'] if song in self.songs_cache else 0

    def show_song(self: Tk, songs: list) -> None:
        if self.song in songs:
            self.after(100, lambda: self.player_canvas.yview_moveto(
                float((songs.index(self.song) * 65) / self.player_content.winfo_height())))
        if self.settings['follow'] == 2:
            self.songs_queue = songs

    def sort_songs(self: Tk, song: str) -> str:
        if song in self.songs_cache:
            return self.songs_cache[song]['title'][:2].lower()
        else:
            return ''

    def toggle_shuffle(self: Tk) -> None:
        if self.settings['shuffle']:
            # change button style
            self.shuffle_button.configure(style='TButton')
            self.settings['shuffle'] = False
            # sort songs
            if self.songs:
                self.songs.sort(key=self.sort_songs)
        else:
            # change button style
            self.shuffle_button.configure(style='second.TButton')
            self.settings['shuffle'] = True
            # shuffle songs
            if self.songs:
                shuffle(self.songs)

    def cache_song(self: Tk, song: str) -> None:
        album_art = self.icons['note']
        song_title: str = splitext(basename(song))[0]
        song_artist: str = 'Unknown'
        album: str = 'Unknown'
        genre: str = 'Unknown'
        song_metadata = None
        search_tokens: str = ''
        if song.endswith('.mp3'):
            song_metadata = MP3(song)
            if 'TIT2' in song_metadata:
                song_title = f'{song_metadata["TIT2"]}'
                search_tokens += f'{song_title} '
            if 'TPE1' in song_metadata:
                song_artist = f'{song_metadata["TPE1"]}'.replace(
                    ',', ' ').replace('&', '')
                search_tokens += f'{song_artist} '
            if 'TALB' in song_metadata:
                album = f'{song_metadata["TALB"]}'
                search_tokens += f'{album} '
            if 'TCON' in song_metadata:
                genre = f'{song_metadata["TCON"]}'
                search_tokens += f'{genre} '
            if 'APIC:' in song_metadata:
                album_art = ImageTk.PhotoImage(Image.open(
                    BytesIO(song_metadata.get('APIC:').data)).resize((25, 25)))
        elif song.endswith('.flac'):
            song_metadata = FLAC(song)
            if 'title' in song_metadata:
                song_title = song_title.join(song_metadata['title'])
                search_tokens += f'{song_title} '
            if 'artist' in song_metadata:
                song_artist = song_artist.join(
                    song_metadata['artist']).replace(',', ' ').replace('&', '')
                search_tokens += f'{song_artist} '
            if 'album' in song_metadata:
                album = album.join(song_metadata['album'])
                search_tokens += f'{album} '
            if song_metadata.pictures:
                album_art = ImageTk.PhotoImage(Image.open(
                    BytesIO(song_metadata.pictures[0].data)).resize((25, 25)))
        elif song.endswith('.ogg'):
            song_metadata = OggVorbis(song)
            if 'title' in song_metadata:
                song_title = song_title.join(song_metadata['title'])
                search_tokens += f'{song_title} '
            if 'comment' in song_metadata:
                song_artist = song_artist.join(
                    song_metadata['comment']).replace(',', ' ').replace('&', '')
                search_tokens += f'{song_artist} '
        # cache data
        self.songs_cache[song] = {'title': song_title, 'artist': song_artist, 'album': album, 'album_art': album_art, 'length': song_metadata.info.length,
                                  'kbps': song_metadata.info.bitrate, 'genre': genre, 'search_tokens': search_tokens.lower().split(), 'plays': 0}
        self.songs_cache[song]['search_tokens'].extend(
            [song_title.lower(), song_artist.lower(), album.lower()])

    def new_song(self: Tk, song: str) -> None:
        self.cache_song(song)
        self.add_song(song)

    def add_song(self: Tk, song: str) -> None:
        try:
            if song in self.song_panels and self.song_panels[song]:
                self.song_panels[song].destroy()
            self.song_panels[song] = ttk.Frame(
                self.player_content, style='second.TFrame')
            ttk.Label(self.song_panels[song], image=self.songs_cache[song]['album_art']).pack(
                side='left', anchor='center', pady=10, padx=10)
            info_frame: ttk.Frame = ttk.Frame(
                self.song_panels[song], style='second.TFrame')
            ttk.Label(info_frame, text=f'{self.songs_cache[song]["title"]}', style='fifth.TLabel').place(
                x=5, y=5)
            ttk.Label(info_frame, text=f'{self.songs_cache[song]["artist"]}', style='sixth.TLabel').place(
                x=5, y=28)
            info_frame.pack(side='left', fill='both', expand=True)
            ttk.Button(self.song_panels[song], image=self.icons['menu'], command=lambda: self.song_menu.show(
                song)).pack(side='right', anchor='center', fill='y', pady=10, padx=(0, 5))
            self.songs_cache[song]['play_pause'] = ttk.Button(
                self.song_panels[song], image=self.icons['play_pause'][0], command=lambda: self.panel_play(song))
            self.songs_cache[song]['play_pause'].pack(
                side='right', anchor='center', fill='y', pady=10, padx=(0, 5))
            self.songs_cache[song]['heart'] = ttk.Button(self.song_panels[song], image=self.icons['heart']
                                                         [song in self.settings['playlists']['Favorites']['Songs']], command=lambda: self.favorites_song(song))
            self.songs_cache[song]['heart'].pack(
                side='right', anchor='center', fill='y', pady=10, padx=5)
        except Exception as err_obj:
            self.log(err_obj)

    def remove_song(self: Tk, song: str) -> None:
        try:
            if song in self.song_panels:
                self.song_panels[song].destroy()
                del self.song_panels[song]
            if song in self.songs_cache:
                del self.songs_cache[song]
            if song in self.library:
                self.library.remove(song)
            if song in self.songs:
                self.songs.remove(song)
            if self.song == song:
                self.song = ''
            if self.song in self.songs_queue:
                self.songs_queue.remove(self.song)
        except Exception as err_obj:
            self.log(err_obj)

    def favorites_song(self: Tk, song: str) -> None:
        if self.library:
            if song in self.settings['playlists']['Favorites']['Songs']:
                self.songs_cache[song]['heart'].configure(
                    image=self.icons['heart'][0])
                self.settings['playlists']['Favorites']['Songs'].remove(song)
                if song == self.song:
                    self.favorite_button.configure(
                        image=self.icons['heart'][0])
            else:
                self.songs_cache[song]['heart'].configure(
                    image=self.icons['heart'][1])
                self.settings['playlists']['Favorites']['Songs'].append(song)
                if song == self.song:
                    self.favorite_button.configure(
                        image=self.icons['heart'][1])

    def update_active_panel(self: Tk, song: str) -> None:
        for active_song in filter(lambda active_song: active_song in self.songs_cache and active_song in self.library, self.active_panels):
            self.songs_cache[active_song]['play_pause'].configure(
                image=self.icons['play_pause'][0])
            self.active_panels.remove(active_song)
        # for active_song in self.active_panels:
        #     if active_song in self.songs_cache:
        #         self.songs_cache[active_song]['play_pause'].configure(image=self.icons['play_pause'][0])
        #         self.active_panels.remove(active_song)
        if song in self.songs_cache and not self.paused and mixer.music.get_busy():
            self.songs_cache[song]['play_pause'].configure(
                image=self.icons['play_pause'][1])
            self.active_panels.append(song)

    def update_play_pause(self: Tk) -> None:
        self.play_button.configure(
            image=self.icons['play_pause'][not self.paused and mixer.music.get_busy()])

    def update_info_panel(self: Tk, song: str) -> None:
        self.favorite_button.configure(
            image=self.icons['heart'][song in self.settings['playlists']['Favorites']['Songs']])
        if song in self.songs_cache:
            self.song_album.configure(
                image=self.songs_cache[song]['album_art'])
            self.song_title.configure(text=self.songs_cache[song]['title'])
            self.song_artist.configure(text=self.songs_cache[song]['artist'])
        else:
            self.song_album.configure(image=None)
            self.song_title.configure(text='')
            self.song_artist.configure(text='')

    def update_progress_info(self: Tk, song: str) -> None:
        minute: float = 0.0
        second: float = 0.0
        minute, second = divmod(self.songs_cache[song]['length'], 60)
        self.time_passed['text'] = '0:00'
        self.song_length['text'] = f'{int(minute)}:{str(int(second)).zfill(2)}'
        self.progress_bar.configure(
            value=0, maximum=self.songs_cache[song]['length'])

    def target_playlist(self: Tk) -> None:
        if self.library:
            self.playlist = self.menu_playlist.get()
            self.songs = self.library.copy(
            ) if self.playlist == 'Library' else self.settings['playlists'][self.playlist]['Songs']
            if self.songs and self.settings['shuffle']:
                shuffle(self.songs)
            if not self.paused and not mixer.music.get_busy():
                self.button_play()

    def init_mixer(self: Tk) -> None:
        try:
            size: int = 1024
            if self.settings['buffer'] == 'Slow':
                size = 2048
            if self.settings['buffer'] == 'Fast':
                size = 512
            mixer.pre_init(44800, -16, 2, size)
            mixer.init()
        except Exception as err_obj:
            self.log(err_obj)

    def mixer_play(self: Tk, song: str, start: float = 0) -> None:
        try:

            if self.settings['last_song'] and self.settings['last_song'] in self.songs_cache and (self.progress_bar['value'] - self.offset) >= (self.songs_cache[self.settings['last_song']]['length'] / self.settings['played_percent']):
                self.songs_cache[self.settings['last_song']]['plays'] += 1
            if exists(song):
                mixer.music.load(song)
                self.offset = start
                mixer.music.play(start=start)
                self.paused = False
                self.song = self.settings['last_song'] = song
                self.update_progress_info(song)
                self.update_active_panel(song)
                self.update_info_panel(song)
                self.update_play_pause()
                if self.after_job:
                    self.after_cancel(self.after_job)
                    self.after_job = None
                if not self.mixer_active:
                    self.mixer_thread()
        except Exception as err_obj:
            self.log(err_obj)

    def mixer_pause(self: Tk) -> None:
        mixer.music.pause()
        self.paused = True
        self.update_active_panel(self.song)
        self.update_play_pause()

    def mixer_unpause(self: Tk) -> None:
        mixer.music.unpause()
        self.paused = False
        self.update_active_panel(self.song)
        self.update_play_pause()

    def panel_play(self: Tk, song: str) -> None:
        if song == self.song and self.paused:
            self.mixer_unpause()
        elif song == self.song and not self.paused and mixer.music.get_busy():
            self.mixer_pause()
        else:
            selected_playlist: str = self.menu_playlist.get()
            if selected_playlist != self.playlist:
                if selected_playlist in ('Library', 'Settings', 'Folders'):
                    self.playlist = 'Library'
                    self.songs = self.library.copy()
                elif selected_playlist in self.settings['playlists']:
                    self.playlist = selected_playlist
                    self.songs = self.settings['playlists'][self.playlist]['Songs'].copy(
                    )
                if self.songs and self.settings['shuffle']:
                    shuffle(self.songs)
            self.mixer_play(song)

    def progress_play(self: Tk, event: Event) -> None:
        self.mixer_play(self.song, (event.x / self.progress_bar.winfo_width())
                        * self.songs_cache[self.song]['length'])

    def button_play(self: Tk) -> None:
        if self.song and self.paused:
            self.mixer_unpause()
        elif self.song and not self.paused and mixer.music.get_busy():
            self.mixer_pause()
        elif self.song in self.songs:
            self.mixer_play(self.song)
        elif self.songs:
            self.mixer_play(self.songs[0])
        elif self.library:
            if self.playlist == 'Library':
                self.songs = self.library.copy()
                if self.settings['shuffle']:
                    shuffle(self.songs)
                if self.song in self.songs:
                    self.mixer_play(self.song)
                else:
                    self.mixer_play(self.songs[0])
            elif self.settings['playlists'][self.playlist]['Songs']:
                self.songs = self.settings['playlists'][self.playlist]['Songs']
                if self.settings['shuffle']:
                    shuffle(self.songs)
                if self.song in self.songs:
                    self.mixer_play(self.song)
                else:
                    self.mixer_play(self.songs[0])

    def mixer_thread(self: Tk) -> None:
        self.mixer_active = True
        if mixer.music.get_busy() and self.song:
            abs_pos: float = mixer.music.get_pos() / 1000
            position: float = abs_pos + self.offset
            self.progress_bar['value'] = position
            self.time_passed['text'] = f'{int(divmod(position, 60)[0])}:{str(int(divmod(position, 60)[1])).zfill(2)}'
            self.after(150, self.mixer_thread)
        elif not mixer.music.get_busy():
            self.mixer_active = False
            self.mixer_after()

    def mixer_after(self: Tk) -> None:
        self.song_length['text'] = self.time_passed['text']
        self.update_active_panel('')
        self.update_play_pause()
        if self.settings['repeat'] == 'One':
            self.after_job = self.after(
                self.settings['crossfade'], self.button_play)
        elif self.settings['repeat'] == 'All':
            self.after_job = self.after(
                self.settings['crossfade'], self.button_next)

    def button_next(self: Tk) -> None:
        if self.song in self.songs:
            new_index: int = self.songs.index(self.song) + 1
            self.song = self.songs[new_index if new_index < len(
                self.songs) else 0]
            self.mixer_play(self.song)
        elif self.songs:
            self.song = self.songs[0]
            self.mixer_play(self.song)
        self.follow_song()

    def button_previous(self: Tk) -> None:
        if mixer.music.get_pos() > 3000:
            self.mixer_play(self.song)
        else:
            if self.song in self.songs:
                new_index: int = self.songs.index(self.song) - 1
                self.song = self.songs[new_index if new_index >= 0 else -1]
                self.mixer_play(self.song)
            elif self.songs:
                self.song = self.songs[-1]
                self.mixer_play(self.song)
            self.follow_song()

    def toggle_volume(self: Tk) -> None:
        if self.muted:
            self.set_volume(self.settings['volume'])
            self.muted = False
        else:
            mixer.music.set_volume(0.0)
            self.muted = True
            self.mute_button.configure(image=self.icons['speaker'][0])

    def set_volume(self: Tk, volume: str) -> None:
        temp_volume: float = float(volume)
        if temp_volume == 0.0:
            self.mute_button.configure(image=self.icons['speaker'][0])
        elif 0.25 >= temp_volume <= 0.5:
            self.mute_button.configure(image=self.icons['speaker'][1])
        elif 0.5 >= temp_volume <= 0.75:
            self.mute_button.configure(image=self.icons['speaker'][2])
        else:
            self.mute_button.configure(image=self.icons['speaker'][3])
        mixer.music.set_volume(temp_volume)
        self.settings['volume'] = temp_volume
        # check if muted
        if self.muted:
            self.muted = False

    def toggle_repeat(self: Tk) -> None:
        if self.settings['repeat'] == 'None':
            self.settings['repeat'] = 'All'
            self.repeat_button.configure(
                image=self.icons['repeat'][0], style='second.TButton')
        elif self.settings['repeat'] == 'All':
            self.repeat_button.configure(image=self.icons['repeat'][1])
            self.settings['repeat'] = 'One'
        else:
            self.settings['repeat'] = 'None'
            self.repeat_button.configure(
                style='TButton', image=self.icons['repeat'][0])

    def follow_song(self: Tk) -> None:
        playlist = self.menu_playlist.get()
        if self.settings['follow'] == 2 and self.song in self.songs_queue and playlist == self.playlist:
            self.player_canvas.yview_moveto(float((self.songs_queue.index(
                self.song) * 65) / self.player_content.winfo_height()))

    def import_settings(self: Tk) -> None:
        try:
            settings_file: str = askopenfilename(
                title='Open a settings file', initialdir='/', filetypes=(('Sounder settings files', '*.json'),))
            if settings_file:
                with open(settings_file, 'r') as data:
                    try:
                        self.settings.update(load(data))
                    except JSONDecodeError as err_obj:
                        self.log(err_obj)
                self.save_settings()
        except Exception as err_obj:
            self.log(err_obj)

    def export_settings(self: Tk) -> None:
        settings_file = asksaveasfile(mode='w', defaultextension='.json', filetypes=(
            ('Sounder settings files', '*.json'),))
        if settings_file:
            dump(self.settings, settings_file)

    def edit_playlist(self: Tk, _: Event) -> None:
        self.playlist_options.lift()
        self.playlist_entry.select_range(0, 'end')
        self.playlist_entry.focus_force()


if __name__ == '__main__':
    Sounder().mainloop()
