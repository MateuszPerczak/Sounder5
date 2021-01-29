try:
    from typing import ClassVar
    from tkinter import Tk, ttk, StringVar, BooleanVar, DoubleVar, Canvas, Event, Toplevel
    from tkinter.filedialog import askdirectory
    from tkinter.messagebox import askyesno
    from os.path import isfile, join, isdir, basename, abspath, join, splitext, dirname, exists
    from os import startfile, listdir, walk# getcwd, listdir, startfile, remove
    from json import load, dump
    from json.decoder import JSONDecodeError
    from logging import basicConfig, error, getLevelName, getLogger, shutdown
    from traceback import format_exc
    from PIL import Image, ImageTk
    from io import BytesIO
    from random import choices, shuffle
    from string import ascii_uppercase, digits
    from Components.SystemTheme import get_theme
    from Components.Debugger import Debugger
    from Components.Setup import SSetup
    from Components.le import compare
    from Components.SongMenu import SongMenu
    from requests import get
    from threading import Thread, active_count, enumerate as enum_threads
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    from re import findall
    from pygame import mixer
    from time import sleep
    from win10toast import ToastNotifier
except ImportError as err:
    exit(err)


class Sounder(Tk):
    def __init__(self: ClassVar) -> None:
        super().__init__()
        # init logging errors
        self.init_logging()
        # hide window
        self.withdraw()
        # configure window
        self.minsize(800, 500)
        self.title('Sounder')
        self.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.bind('<F12>', lambda _: Debugger(self))
        # init notifications
        self.init_notifications()
        # init settings
        self.init_settings()
        self.apply_settings()
        # init layout
        self.init_layout()
        # load icons
        self.load_icons()
        # init theme
        self.apply_theme()
        # init ui
        self.init_ui()
        # init player
        self.init_player()
        # show window
        self.deiconify()

    def init_logging(self: ClassVar) -> None:
        # logging error messages
        basicConfig(filename=f'Resources\\Dumps\\dump.txt', level=40)

    def log(self: ClassVar, err_obj: ClassVar) -> None:
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

    def init_notifications(self: ClassVar) -> None:
        self.toaster: object = ToastNotifier()

    def init_settings(self: ClassVar) -> None:
        try:
            # variables
            default_settings: dict = {'shuffle': False, 'start_playback': False, 'playlist': 'Library', 'repeat': 'None', 'buffer': 'Normal', 'last_song': '', 'volume': 0.5, 'sort_by': 'A-Z', 'scan_subfolders': False, 'geometry': '800x500', 'wheel_acceleration': 1.0, 'updates': True, 'folders': [], 'use_system_theme': True, 'theme': 'Light', 'page': 'Library', 'playlists': {'Favorites': {'Name': 'Favorites', 'Songs': []}}}
            self.settings: dict = {}
            self.version: tuple = ('0.6.2', '290121')
            # load settings
            if isfile('Resources\\Settings\\Settings.json'):
                with open('Resources\\Settings\\Settings.json', 'r') as data:
                    try:
                        self.settings = load(data)
                    except JSONDecodeError as err_obj:
                        self.settings = default_settings
            else:
                self.settings = default_settings
                # open sounder configurator
                SSetup(self, self.settings).mainloop()  
            # verify settings
            for key in default_settings:
                self.settings[key] =  self.settings.get(key, default_settings[key])
            # verify playlist
            if not 'Favorites' in self.settings['playlists']: self.settings['playlists']['Favorites'] = {'Name': 'Favorites', 'Songs': []}
        except Exception as err_obj:
            self.log(err_obj)

    def apply_settings(self: ClassVar) -> None:
        # check theme
        if self.settings['use_system_theme']:
            self.settings['theme']: str = get_theme()
        # check for updates
        if self.settings['updates']:
            self.after(5000, self.update_thread)
        # bind escape to root window 
        self.bind('<Escape>', lambda _: self.focus_set())
        # bind scroll to content
        self.bind('<MouseWheel>', self.on_wheel)
        # apply geometry
        self.geometry(self.settings['geometry'])

    def save_settings(self: ClassVar) -> None:
        # save last page
        self.settings['page'] = self.menu_option.get()
        # save player state ...
        # save app geometry
        self.settings['geometry'] = f'{self.geometry()}'
        # save active playlists
        self.settings['playlist'] = self.playlist
        try:
            with open('Resources\\Settings\\Settings.json', 'w') as data:
                dump(self.settings, data)
        except Exception as err_obj:
            self.log(err_obj)

    def restore_default(self: ClassVar) -> None:
        if askyesno('Restore default configuration', 'Are you sure you want to restore the default configuration?', icon='warning'):
            self.settings: dict = {}
            self.exit_app()

    def init_layout(self: ClassVar) -> None:
        # init theme object
        self.layout: ClassVar = ttk.Style()
        # set theme to clam
        self.layout.theme_use('clam')
        # button
        self.layout.layout('TButton', [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # radiobutton
        self.layout.layout('TRadiobutton', [('Radiobutton.padding', {'sticky': 'nswe', 'children': [('Radiobutton.label', {'sticky': 'nswe'})]})])
        # scrollbar
        self.layout.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
        # entry
        self.layout.layout('TEntry', [('Entry.padding', {'sticky': 'nswe', 'children': [('Entry.textarea', {'sticky': 'nswe'})]})])
        
    def apply_theme(self: ClassVar) -> None:
        theme: dict = {'Dark': ['#111', '#212121', '#333', '#fff'], 'Light': ['#eee', '#fff', '#aaa', '#000']}
        # window 
        self.configure(background=theme[self.settings['theme']][1])
        # frame
        self.layout.configure('TFrame', background=theme[self.settings['theme']][1])
        self.layout.configure('second.TFrame', background=theme[self.settings['theme']][0])
        # label
        self.layout.configure('TLabel', background=theme[self.settings['theme']][0], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3])
        self.layout.configure('second.TLabel', background=theme[self.settings['theme']][1], font=('catamaran 20 bold'))
        self.layout.configure('third.TLabel', background=theme[self.settings['theme']][1])
        self.layout.configure('fourth.TLabel', background=theme[self.settings['theme']][1], font=('catamaran 16 bold'))
        self.layout.configure('fifth.TLabel', background=theme[self.settings['theme']][0], font=('catamaran 10 bold'))
        self.layout.configure('sixth.TLabel', background=theme[self.settings['theme']][0], font=('catamaran 8 bold'))
        # radiobutton
        self.layout.configure('TRadiobutton', background=theme[self.settings['theme']][0], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w', padding=5, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('second.TRadiobutton', anchor='c', padding=5, width=6)
        self.layout.configure('third.TRadiobutton', anchor='c', padding=5, width=8)
        self.layout.configure('fourth.TRadiobutton', anchor='c')
        self.layout.configure('fifth.TRadiobutton', font=('catamaran 12 bold'), background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3], anchor='c', padding=4, width=6)
        self.layout.map('fifth.TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        # button
        self.layout.configure('TButton', background=theme[self.settings['theme']][0], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w')
        self.layout.map('TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('second.TButton', background=theme[self.settings['theme']][1], anchor='c')
        self.layout.map('second.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        self.layout.configure('third.TButton', background=theme[self.settings['theme']][0], anchor='c')
        self.layout.map('third.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('fourth.TButton', anchor='c', background=theme[self.settings['theme']][1], width=20)
        self.layout.map('fourth.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        # scrollbar
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background=theme[self.settings['theme']][1], darkcolor=theme[self.settings['theme']][1], lightcolor=theme[self.settings['theme']][1], troughcolor=theme[self.settings['theme']][1], bordercolor=theme[self.settings['theme']][1])
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][0]), ('!active', theme[self.settings['theme']][0])])   
        # scale
        self.layout.map('Horizontal.TScale', background=[('pressed', '!disabled', theme[self.settings['theme']][2]), ('active', theme[self.settings['theme']][2])])
        # self.layout.configure('Horizontal.TScale', troughcolor='#151515', background='#333', relief="flat", gripcount=0, darkcolor="#151515", lightcolor="#151515", bordercolor='#151515')
        self.layout.configure('Horizontal.TScale', troughcolor=theme[self.settings['theme']][0], background=theme[self.settings['theme']][1], relief='flat', gripcount=0, darkcolor=theme[self.settings['theme']][0], lightcolor=theme[self.settings['theme']][0], bordercolor=theme[self.settings['theme']][0])
        # entry
        self.layout.configure('TEntry', background=theme[self.settings['theme']][1],  foreground=theme[self.settings['theme']][3], fieldbackground=theme[self.settings['theme']][0], selectforeground=theme[self.settings['theme']][3], selectbackground=theme[self.settings['theme']][2])
        self.layout.map('TEntry', foreground=[('active', '!disabled', 'disabled', theme[self.settings['theme']][3])]) 
        self.layout.configure('second.TEntry', background=theme[self.settings['theme']][0])
        # progressbar
        self.layout.configure("Horizontal.TProgressbar", background=theme[self.settings['theme']][1], lightcolor=theme[self.settings['theme']][0], darkcolor=theme[self.settings['theme']][0], bordercolor=theme[self.settings['theme']][0], troughcolor=theme[self.settings['theme']][0], thickness=2)

    def load_icons(self: ClassVar) -> None:
        self.icons: dict = {
            'error': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\error.png').resize((100, 100))),
            'library': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\library.png').resize((25, 25))),
            'folder': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\folder.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\music_folder.png').resize((25, 25)))),
            'settings': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\settings.png').resize((25, 25))),
            'plus': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\plus.png').resize((25, 25))),
            'heart': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\heart_empty.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\heart_filled.png').resize((25, 25)))),
            'delete': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\delete.png').resize((25, 25))),
            'playlist': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\playlist.png').resize((25, 25))),
            'play_pause': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\play.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\pause.png').resize((25, 25)))),
            'next': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\next.png').resize((25, 25))),
            'previous': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\previous.png').resize((25, 25))),
            'repeat': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\repeat.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\repeat_one.png').resize((25, 25)))),
            'shuffle': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\shuffle.png').resize((25, 25))),
            'edit': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\edit.png').resize((25, 25))),
            'menu': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\menu.png').resize((25, 25))),
            'clock': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\clock.png').resize((25, 25))),
            'note': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\note.png').resize((25, 25))),
            'arrow': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\left.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\right.png').resize((25, 25)))),
            'checkmark': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\checkmark.png').resize((25, 25))),
            'restore': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\restore.png').resize((25, 25))),
            'brush': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\brush.png').resize((25, 25))),
            'info': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\info.png').resize((25, 25))),
            'window': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\window.png').resize((25, 25))),
            'user': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\user.png').resize((25, 25))),
            'icons8': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\icons8.png').resize((25, 25))),
            'code': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\code.png').resize((25, 25))),
            'logo': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\logo.png').resize((25, 25))),
            'download': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\download.png').resize((25, 25))),
            'wheel': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\wheel.png').resize((25, 25))),
            'search': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\search.png').resize((25, 25))),
            'filter': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\filter.png').resize((25, 25))),
            'speaker': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\muted.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\low_volume.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\med_volume.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\max_volume.png').resize((25, 25)))),
            'buffer': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\buffer.png').resize((25, 25))),
            'trash': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\trash.png').resize((25, 25))),
            'select': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\select.png').resize((25, 25))),
            'power': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\power.png').resize((25, 25))),
            'sort': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\no_sort.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\normal_sort.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\reversed_sort.png').resize((25, 25))))
            }
        self.iconphoto(False, self.icons['logo'])

    def init_ui(self: ClassVar) -> None:
        # ui variables
        self.menu_option: StringVar = StringVar(value=self.settings['page'])
        self.menu_playlist: StringVar = StringVar(value=self.settings['page'])
        self.buffer: StringVar = StringVar(value=self.settings['buffer'])
        self.muted: bool = True if self.settings['volume'] == 0.0 else False
        self.start_playback: BooleanVar = BooleanVar(value=self.settings['start_playback'])
        self.sort_by: StringVar = StringVar(value=self.settings['sort_by'])
        self.last_panel: str = ''
        self.folder_panels: dict = {}
        self.song_panels: dict = {}
        self.settings_panels: tuple = ()
        # theme
        self.theme: StringVar = StringVar()
        if self.settings['use_system_theme']:
            self.theme.set('System')
        else:
            self.theme.set(self.settings['theme'])
        # update
        self.updates: BooleanVar = BooleanVar(value=self.settings['updates'])
        # wheel acceleration
        self.wheel_acceleration: DoubleVar = DoubleVar(value=self.settings['wheel_acceleration'])
        # scan subfolders
        self.scan_subfolders: BooleanVar = BooleanVar(value=self.settings['scan_subfolders'])
        # player panel
        self.player_panel: ClassVar = ttk.Frame(self)
        # top panel
        player_top_panel: ClassVar = ttk.Frame(self.player_panel)
        # menu panel 
        self.menu_panel: ClassVar = ttk.Frame(player_top_panel, style='second.TFrame')
        ttk.Radiobutton(self.menu_panel, image=self.icons['library'], text='Library', compound='left', value='Library', variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=(10, 0))
        ttk.Radiobutton(self.menu_panel, image=self.icons['folder'][1], text='Folders', compound='left', value='Folders', variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=10)
        ttk.Radiobutton(self.menu_panel, image=self.icons['settings'], text='Settings', compound='left', value='Settings', variable=self.menu_option, command=self.show_panel).pack(side='bottom', fill='x', padx=10, pady=(0, 10))
        ttk.Label(self.menu_panel, text='Playlists').pack(side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Button(self.menu_panel, image=self.icons['plus'], text='Add playlist', compound='left', command=self.add_playlist).pack(side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Radiobutton(self.menu_panel, image=self.icons['heart'][1], text='Favorites', compound='left', value='Favorites', variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10)
        # add playlist from settings
        for playlist in self.settings['playlists']:
            if playlist == 'Favorites': continue
            ttk.Radiobutton(self.menu_panel, image=self.icons['playlist'], text=self.settings['playlists'][playlist]['Name'], compound='left', value=playlist, style='menu.TRadiobutton', variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
        self.menu_panel.pack(side='left', fill='both')
        # player scrollbar
        player_content_scroll: ClassVar = ttk.Scrollbar(player_top_panel, orient='vertical')
        player_content_scroll.pack(side='right', fill='y')
        # options panel
        player_options_panel: ClassVar = ttk.Frame(player_top_panel)
        # update options panel
        self.update_panel: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.update_panel, image=self.icons['download'], text='Update available!', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.update_panel, image=self.icons['delete'], text='Remind me later', style='second.TButton', compound='left', command=self.snooze_update).pack(side='right', anchor='c', padx=(0, 15))
        ttk.Button(self.update_panel, image=self.icons['checkmark'], text='Update now', style='second.TButton', compound='left').pack(side='right', anchor='c', padx=(0, 5))
        self.update_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # playlist panel
        self.playlist_panel: ClassVar = ttk.Frame(player_options_panel)
        # playlist arbitrary name
        self.playlist_an: ClassVar = ttk.Label(self.playlist_panel, image=None, text='', style='fourth.TLabel', compound='left')
        self.playlist_an.pack(side='left', anchor='c', padx=(10, 0))
        self.playlist_an.bind('<Double-Button-1>', lambda _: self.playlist_options.lift())
        # playlist menu button
        ttk.Button(self.playlist_panel, image=self.icons['menu'], style='second.TButton', command=lambda: self.playlist_options.lift()).pack(side='right', anchor='c', padx=(0, 15))
        ttk.Button(self.playlist_panel, image=self.icons['select'], style='second.TButton', command=self.target_playlist).pack(side='right', anchor='c', padx=(0, 5))
        ttk.Button(self.playlist_panel, image=self.icons['filter'], style='second.TButton', command=lambda: self.sort_options.lift()).pack(side='right', anchor='c', padx=(0, 5))
        self.playlist_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # playlist options
        self.playlist_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.playlist_options, image=self.icons['edit'], style='third.TLabel').pack(side='left', anchor='c', padx=(10, 1))
        # playlist entry
        self.playlist_entry: ClassVar = ttk.Entry(self.playlist_options, exportselection=False, font=('catamaran 16 bold'))
        self.playlist_entry.pack(side='left', anchor='c')
        self.playlist_entry.bind('<Return>', self.rename_playlist)
        ttk.Button(self.playlist_options, image=self.icons['arrow'][0], style='second.TButton', command=lambda: self.playlist_panel.lift()).pack(side='right', anchor='c', padx=(10, 15))
        self.playlist_remove: ClassVar = ttk.Button(self.playlist_options, text='Remove playlist', image=self.icons['delete'], compound='left', style='second.TButton', command=self.remove_playlist)
        self.playlist_remove.pack(side='right', anchor='c', padx=(10, 0))
        self.playlist_options.place(x=0, y=0, relwidth=1, relheight=1)
        # folder options
        self.folder_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.folder_options, image=self.icons['folder'][1], text='Folders', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.folder_options, image=self.icons['plus'], text='Add folder', compound='left', style='second.TButton', command=self.new_folder).pack(side='right', anchor='c', padx=(10, 15))
        self.folder_options.place(x=0, y=0, relwidth=1, relheight=1)
        # settings options
        self.settings_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.settings_options, image=self.icons['settings'], text='Settings', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.settings_options, image=self.icons['restore'], text='Restore default settings', compound='left', style='second.TButton', command=self.restore_default).pack(side='right', anchor='c', padx=(10, 15))
        ttk.Button(self.settings_options, image=self.icons['checkmark'], text='Save changes', compound='left', style='second.TButton', command=self.save_settings).pack(side='right', anchor='c', padx=(10, 0))
        self.settings_options.place(x=0, y=0, relwidth=1, relheight=1)
        # library options
        self.library_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.library_options, image=self.icons['library'], text='Library', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.library_options, image=self.icons['filter'], style='second.TButton', command=lambda: self.sort_options.lift()).pack(side='right', anchor='c', padx=(0, 15))
        ttk.Button(self.library_options, image=self.icons['select'], style='second.TButton', command=self.target_playlist).pack(side='right', anchor='c', padx=(0, 5))
        # library search bar
        search_panel: ClassVar = ttk.Frame(self.library_options)
        self.lib_search: ClassVar = ttk.Button(search_panel, image=self.icons['search'], style='second.TButton', command=self.open_search)
        self.lib_search.pack(side='right', anchor='c')
        self.lib_entry: ClassVar =ttk.Entry(search_panel, exportselection=False, font=('catamaran 15 bold'), width=12, style='second.TEntry')
        self.lib_entry.bind('<Return>', self.search)
        search_panel.pack(side='right', anchor='c', padx=(0, 5))
        self.library_options.place(x=0, y=0, relwidth=1, relheight=1)
        # sort options
        self.sort_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.sort_options, image=self.icons['filter'], text='Sort by', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.sort_options, image=self.icons['arrow'][0], style='second.TButton', command=lambda: self.sort_options.lower()).pack(side='right', anchor='c', padx=(0, 15))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][0], text='None', compound='left', style='fifth.TRadiobutton', value='#', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='c', padx=(0, 10))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][2], text='Name', compound='left', style='fifth.TRadiobutton', value='Z-A', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='c', padx=(0, 5))
        ttk.Radiobutton(self.sort_options, image=self.icons['sort'][1], text='Name', compound='left', style='fifth.TRadiobutton', value='A-Z', variable=self.sort_by, command=self.change_sort).pack(side='right', anchor='c', padx=(0, 5))
        self.sort_options.place(x=0, y=0, relwidth=1, relheight=1)
        player_options_panel.pack(side='top', fill='x', ipady=28.5)
        # player content
        self.player_canvas: ClassVar = Canvas(player_top_panel, background=self['background'], bd=0, highlightthickness=0, yscrollcommand=player_content_scroll.set, takefocus=False)
        # link scrollbar to canvas
        player_content_scroll.configure(command=self.player_canvas.yview)
        # player content
        self.player_content: ClassVar = ttk.Frame(self.player_canvas)
        self.player_content.bind('<Configure>', lambda _: self.player_canvas.configure(scrollregion=self.player_canvas.bbox("all")))
        self.content_window: ClassVar = self.player_canvas.create_window((0, 0), window=self.player_content, anchor='nw')
        self.player_canvas.bind('<Configure>', lambda _: self.player_canvas.itemconfigure(self.content_window, width=self.player_canvas.winfo_width(), height=0))
        self.player_canvas.pack(side='top', fill='both', expand=True)
        player_top_panel.pack(side='top', fill='both', expand=True)
        # add folders from settings
        for folder in self.settings['folders']:
            self.add_folder(abspath(folder))
        # settings panels
        # theme
        settings_theme: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        theme_panel: ClassVar = ttk.Frame(settings_theme, style='second.TFrame')
        ttk.Label(theme_panel, image=self.icons['brush'], text='Theme', style='TLabel', compound='left').pack(side='left', anchor='c', fill='y')
        ttk.Radiobutton(theme_panel, text='System', style='second.TRadiobutton', value='System', variable=self.theme, command=self.change_theme).pack(side='right', anchor='c')
        ttk.Radiobutton(theme_panel, text='Light', style='second.TRadiobutton', value='Light', variable=self.theme, command=self.change_theme).pack(side='right', anchor='c', padx=(10, 10))
        ttk.Radiobutton(theme_panel, text='Dark', style='second.TRadiobutton', value='Dark', variable=self.theme, command=self.change_theme).pack(side='right', anchor='c')
        theme_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_theme, image=self.icons['info'], text='Note: You need to restart the application to see any changes!', compound='left').pack(side='top', fill='x', padx=10, pady=(0, 10))
        # acceleration
        settings_acceleration: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        ttk.Label(settings_acceleration, image=self.icons['wheel'], text='Wheel acceleration', compound='left').pack(side='left', anchor='c', fill='y', pady=10, padx=10)
        ttk.Label(settings_acceleration, text='Fast').pack(side='right', anchor='c', fill='y', pady=10, padx=10)
        ttk.Scale(settings_acceleration, variable=self.wheel_acceleration, from_=1, to=8, command=self.change_acceleration).pack(side='right', anchor='c', fill='x', ipadx=20)
        ttk.Label(settings_acceleration, text='Slow').pack(side='right', anchor='c', fill='y', pady=10, padx=10)
        # updates
        settings_updates: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        ttk.Label(settings_updates, image=self.icons['download'], text='Check for updates', compound='left').pack(side='left', anchor='c', fill='y', pady=10, padx=10)
        ttk.Radiobutton(settings_updates, text='No', style='second.TRadiobutton', value=False, variable=self.updates, command=self.change_updates).pack(side='right', anchor='c', padx=(10, 10))
        ttk.Radiobutton(settings_updates, text='Yes', style='second.TRadiobutton', value=True, variable=self.updates, command=self.change_updates).pack(side='right', anchor='c')
        # about
        settings_about: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        ttk.Label(settings_about, image=self.icons['logo'], text='About Sounder', compound='left').pack(side='top', anchor='c', fill='x', padx=10, pady=10)
        ttk.Label(settings_about, image=self.icons['window'], text=f'Version: {self.version[0]} Build: {self.version[1]}', compound='left').pack(side='top', anchor='c', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['user'], text='Author: Mateusz Perczak', compound='left').pack(side='top', anchor='c', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['icons8'], text='Icons: Icons8', compound='left').pack(side='top', anchor='c', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_about, image=self.icons['code'], text='UI: LUI V2', compound='left').pack(side='top', anchor='c', fill='x', padx=10, pady=(0, 10))
        # folders
        settings_subfolders: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        subfolders_panel: ClassVar = ttk.Frame(settings_subfolders, style='second.TFrame')
        ttk.Label(subfolders_panel, image=self.icons['folder'][0], text='Scan subfolders', compound='left').pack(side='left', anchor='c', fill='y')
        ttk.Radiobutton(subfolders_panel, text='No', style='second.TRadiobutton', value=False, variable=self.scan_subfolders, command=self.change_subfolders).pack(side='right', anchor='c', padx=(10, 0))
        ttk.Radiobutton(subfolders_panel, text='Yes', style='second.TRadiobutton', value=True, variable=self.scan_subfolders, command=self.change_subfolders).pack(side='right', anchor='c')
        subfolders_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_subfolders, image=self.icons['info'], text='Note: Scanning subfolders may affect performance!', compound='left').pack(side='top', fill='x', padx=10, pady=(0, 10))
        # mixer buffer
        settings_buffer: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        buffer_panel: ClassVar = ttk.Frame(settings_buffer, style='second.TFrame')
        ttk.Label(buffer_panel, image=self.icons['buffer'], text='Player buffer mode', compound='left').pack(side='left', anchor='c', fill='y')
        ttk.Radiobutton(buffer_panel, text='Fastest', style='third.TRadiobutton', value='Fast', variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='c')
        ttk.Radiobutton(buffer_panel, text='Default', style='third.TRadiobutton', value='Normal', variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='c', padx=(10, 10))
        ttk.Radiobutton(buffer_panel, text='Slowest', style='third.TRadiobutton', value='Slow', variable=self.buffer, command=self.change_buffer).pack(side='right', anchor='c')
        buffer_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_buffer, image=self.icons['info'], text='Note: Setting buffet to fastest reduces lag but may increase underturns!', compound='left').pack(side='top', fill='x', padx=10, pady=(0, 10))
        ttk.Label(settings_buffer, image=self.icons['info'], text='Note: You need to restart the application to see any changes!', compound='left').pack(side='top', fill='x', padx=10, pady=(0, 10))
        # startup
        settings_startup: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        ttk.Label(settings_startup, image=self.icons['power'], text='On startup', compound='left').pack(side='left', anchor='c', fill='y', pady=10, padx=10)
        ttk.Radiobutton(settings_startup, text='Do nothing', style='fourth.TRadiobutton', value=False, variable=self.start_playback, command=self.change_playback).pack(side='right', anchor='c', padx=(0, 10))
        ttk.Radiobutton(settings_startup, text='Start playback', style='fourth.TRadiobutton', value=True, variable=self.start_playback, command=self.change_playback).pack(side='right', anchor='c', padx=(0, 10))
        # panels variable
        self.settings_panels = (settings_acceleration, settings_theme, settings_startup, settings_subfolders, settings_updates, settings_buffer, settings_about)
        # bottom panel
        player_bot_panel: ClassVar = ttk.Frame(self.player_panel, style='second.TFrame')
        # buttons, song name, etc ...
        center_panel: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        self.play_button: ClassVar = ttk.Button(center_panel, image=self.icons['play_pause'][0], takefocus=False, command=self.button_play)
        self.play_button.place(relx=0.5, rely=0.5, anchor='center')
        # next button
        ttk.Button(center_panel, image=self.icons['next'], takefocus=False, command=self.button_next).place(relx=0.65, rely=0.5, anchor='center')
        # previous button
        ttk.Button(center_panel, image=self.icons['previous'], takefocus=False, command=self.button_previous).place(relx=0.35, rely=0.5, anchor='center')
        # shuffle button
        self.shuffle_button: ClassVar = ttk.Button(center_panel, image=self.icons['shuffle'], takefocus=False, command=self.toggle_shuffle)
        self.shuffle_button.place(relx=0.15, rely=0.5, anchor='center')
        if self.settings['shuffle']: self.shuffle_button.configure(style='second.TButton')
        else: self.shuffle_button.configure(style='TButton')
        # repeat button
        self.repeat_button: ClassVar = ttk.Button(center_panel, takefocus=False, command=self.toggle_repeat)
        if self.settings['repeat'] == 'None': self.repeat_button.configure(image=self.icons['repeat'][0])
        elif self.settings['repeat'] == 'All': self.repeat_button.configure(image=self.icons['repeat'][0], style='second.TButton')
        else: self.repeat_button.configure(image=self.icons['repeat'][1], style='second.TButton')
        self.repeat_button.place(relx=0.85, rely=0.5, anchor='center')
        center_panel.place(relx=0.5, y=10, width=350, height=48, anchor='n')
        volume_panel: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        # mute button
        self.mute_button: ClassVar = ttk.Button(volume_panel, image=self.icons['speaker'][0], takefocus=False, command=self.toggle_volume)
        self.mute_button.pack(side='left', anchor='center', padx=5)
        # volume bar
        self.volume_bar: ClassVar = ttk.Scale(volume_panel, orient='horizontal', from_=0, to=1, command=self.set_volume)
        self.volume_bar.pack(side='left', anchor='center', padx=5, fill='x', expand=True)
        volume_panel.place(relx=1, y=10, relwidth=0.22, height=48, anchor='ne')
        player_bot_panel.pack(side='top', fill='x', ipady=45)
        self.player_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # left frame
        info_panel: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        self.song_album: ClassVar = ttk.Label(info_panel)
        self.song_album.pack(side='left', padx=10, anchor='c')
        info_frame: ClassVar = ttk.Frame(info_panel, style='second.TFrame')
        self.song_title: ClassVar = ttk.Label(info_frame, text='', style='fifth.TLabel')
        self.song_title.place(x=0, y=4)
        self.song_artist: ClassVar = ttk.Label(info_frame, text='', style='sixth.TLabel')
        self.song_artist.place(x=0, y=24)
        info_frame.pack(side='left', fill='both', expand=True)
        info_panel.place(relx=0, y=10, relwidth=0.22, height=48, anchor='nw')
        info_panel.bind('<Expose>', self.update_title_length)
        # bottom frame
        progress_frame: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        # time passed
        self.time_passed: ClassVar = ttk.Label(progress_frame, text='--:--', anchor='center', justify='center', style='sixth.TLabel')
        self.time_passed.pack(side='left', ipadx=10)
        # progress bar
        self.progress_bar: ClassVar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side='left', fill='x', expand=True)
        # song length
        self.song_length: ClassVar = ttk.Label(progress_frame, text='--:--', anchor='center', justify='center', style='sixth.TLabel')
        self.song_length.pack(side='right', ipadx=10)
        progress_frame.place(relx=0.5, y=68, relwidth=1, height=20, anchor='n')
        # error panel
        self.error_panel: ClassVar = ttk.Frame(self)
        error_content: ClassVar = ttk.Frame(self.error_panel)
        ttk.Label(error_content, image=self.icons['error'], text='Something went wrong', compound='top', style='second.TLabel').pack(side='top')
        self.error_label: ClassVar = ttk.Label(error_content, text='We are unable to display the error message!', style='third.TLabel')
        self.error_label.pack(side='top')
        ttk.Button(error_content, text='OK', style='third.TButton', command=self.exit_app).pack(side='top', pady=(50, 0), padx=10)
        ttk.Button(error_content, text='Open Logs', style='third.TButton', command=self.open_logs).pack(side='top', pady=(10, 0), padx=10)
        error_content.place(relx=.5, rely=.5, anchor='c')
        ttk.Label(self.error_panel, text=f'version: {self.version[0]} [build: {self.version[1]}]', style='third.TLabel').pack(side='bottom', anchor='w', padx=10, pady=5)
        self.error_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # show main panel
        self.player_panel.lift()
        # info panels
        self.search_panel: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        ttk.Label(self.search_panel, image=self.icons['info'], text='No songs found!', compound='left').pack(side='left', anchor='c', fill='y', pady=10, padx=10)

    def init_player(self: ClassVar) -> None:
        # variables
        self.library: list = []
        self.songs_cache: dict = {}
        self.active_panels: list = []
        self.paused: bool = False
        self.playlist: str = self.settings['playlist']
        self.songs: list = []
        # set last song 
        self.song: str = self.settings['last_song']
        # init mixer
        self.init_mixer()
        # scan folders
        self.scan_folders()
        # verify playlists
        self.verify_playlist()
        # show last panel
        self.show_panel() if self.settings['page'] in ('Library', 'Folders', 'Settings') else self.show_playlist()
        # load last song info
        self.update_info_panel(self.song)
        # restore volume
        self.volume_bar.set(self.settings['volume'])
        # song menu
        self.song_menu: ClassVar = SongMenu(self)
        # mixer thread
        self.mixer_active: bool = False
        if self.settings['start_playback']:
            self.after(200, self.button_play)

    def exit_app(self: ClassVar) -> None:
        self.withdraw()
        self.save_settings()
        self.destroy()

    def show_panel(self: ClassVar) -> None:
        target_panel: str = self.menu_option.get()
        self.menu_playlist.set(target_panel)
        if target_panel == 'Library':
            self.library_options.lift()
        elif target_panel == 'Folders':
            self.folder_options.lift()
        elif target_panel == 'Settings':
            self.settings_options.lift()
        self.show_panels(target_panel)

    def show_panels(self: ClassVar, panel: str) -> None:
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
                if self.search_panel.winfo_ismapped():
                    self.search_panel.pack_forget()
            # pack
            if panel == 'Folders':
                for folder in self.folder_panels:
                    if not self.folder_panels[folder].winfo_ismapped():
                        self.folder_panels[folder].pack(side='top', fill='x', pady=5, padx=10)
            if panel == 'Settings':
                for setting in self.settings_panels:
                    if not setting.winfo_ismapped():
                        setting.pack(side='top', fill='x', pady=5, padx=10)
            if panel == 'Library':
                self.sort_panels('', self.library)
            if panel in self.settings['playlists']:
                self.sort_panels('', self.settings['playlists'][panel]['Songs'])
        self.last_panel = panel

    def open_logs(self: ClassVar) -> None:
        if isfile('Resources\\Dumps\\dump.txt'): startfile('Resources\\Dumps\\dump.txt')

    def on_wheel(self: ClassVar, event: Event) -> None:
        self.player_canvas.yview_scroll(int(-self.settings['wheel_acceleration']*(event.delta/120)), 'units')

    def show_playlist(self: ClassVar) -> None:
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

    def update_playlist(self: ClassVar, selected_playlist: str) -> None:
        if selected_playlist in self.settings['playlists']:
            # update playlist info
            self.playlist_an['text'] = self.settings['playlists'][selected_playlist]['Name']
            # update entry
            self.playlist_entry.state(['!disabled'])
            self.playlist_entry.delete(0, 'end')
            self.playlist_entry.insert(0, self.settings['playlists'][selected_playlist]['Name'])
            # change icon acording to playlist type and disable some buttons
            if selected_playlist == 'Favorites':
                self.playlist_an['image'] = self.icons['heart'][1]
                # disable button
                self.playlist_remove.state(['disabled'])
                # disable entry
                self.playlist_entry.state(['disabled'])
                self.playlist_entry.configure(cursor='no')
            else:
                self.playlist_an['image'] = self.icons['playlist']
                self.playlist_entry.configure(cursor='ibeam')
                # enable button
                self.playlist_remove.state(['!disabled'])

    def add_playlist(self: ClassVar) -> None:
        playlist_id: str = ''.join(choices(ascii_uppercase + digits, k=4))
        if not playlist_id in self.settings['playlists']:
            self.settings['playlists'][playlist_id]: dict = {'Name': f'Playlist {len(self.settings["playlists"])}', 'Songs': []}
            ttk.Radiobutton(self.menu_panel, image=self.icons['playlist'], text=self.settings['playlists'][playlist_id]['Name'], compound='left', value=playlist_id, variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
            self.song_menu.append(playlist_id)
        
    def remove_playlist(self):
        try:
            if askyesno('Remove playlist', 'Are you sure you want to remove this playlist?\nThis cannot be undone!', icon='warning'):
                selected_playlist: str = self.menu_playlist.get()
                playlist_list: list = list(self.settings['playlists'].keys())
                if selected_playlist in self.settings['playlists'] and selected_playlist != 'Favorites':
                    playlist_list.remove(selected_playlist)
                    # selects last playlist
                    self.menu_playlist.set(playlist_list[len(playlist_list) - 1])
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

    def get_playlist_button(self: ClassVar, playlist: str) -> ClassVar:
        for widget in self.menu_panel.winfo_children():
            if widget.winfo_class() == 'TRadiobutton' and widget['text'] == self.settings['playlists'][playlist]['Name']:
                return widget

    def rename_playlist(self: ClassVar, _) -> None:
        try:
            selected_playlist: str = self.menu_playlist.get()
            new_name: str = self.playlist_entry.get()
            if selected_playlist in self.settings['playlists'] and not selected_playlist == 'Favorites' and new_name.rstrip():
                self.get_playlist_button(selected_playlist)['text'] = new_name[:14]
                self.settings['playlists'][selected_playlist]['Name'] = new_name[:14]
                self.song_menu.rename(selected_playlist, new_name[:14])
                self.playlist_panel.lift()
            else:
                print('error while renaming playlist')
            self.update_playlist(selected_playlist)
        except Exception as err_obj:
            self.log(err_obj)

    def verify_playlist(self: ClassVar) -> None:
        try:
            for playlist in self.settings['playlists']:
                for song in self.settings['playlists'][playlist]['Songs']:
                    if song not in self.library:
                        self.settings['playlists'][playlist]['Songs'].remove(song)
        except Exception as err_obj:
            self.log(err_obj)

    def new_folder(self: ClassVar) -> None:
        new_dir: str = askdirectory()
        if new_dir and new_dir not in self.settings['folders']:
            new_dir = abspath(new_dir)
            self.settings['folders'].append(new_dir)
            self.add_folder(new_dir)
            self.folder_panels[new_dir].pack(side='top', fill='both', expand=True, pady=5, padx=10)
            Thread(target=self.scan_folders, daemon=True).start()

    def add_folder(self: ClassVar, path: str) -> None:
        try:
            self.folder_panels[path]: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
            path_label: ClassVar = ttk.Label(self.folder_panels[path], image=self.icons['folder'][0], text=basename(path), compound='left')
            path_label.pack(side='left', anchor='c', fill='y', pady=10, padx=10)
            ttk.Button(self.folder_panels[path], image=self.icons['delete'], takefocus=False, command=lambda: self.remove_folder(path)).pack(side='right', padx=10, anchor='c')
            self.folder_panels[path].bind('<Leave>', lambda _:path_label.configure(text=basename(path)))
            self.folder_panels[path].bind('<Enter>', lambda _:path_label.configure(text=path))
        except Exception as err_obj:
            self.log(err_obj)

    def remove_folder(self: ClassVar, path: str) -> None:
        if askyesno('Remove folder', 'Are you sure you want to remove this folder?', icon='warning') and path in self.settings['folders']:
            self.folder_panels[path].destroy()
            self.settings['folders'].remove(path)
            self.remove_songs(path)
            del self.folder_panels[path]

    def remove_songs(self: ClassVar, path: str) -> None:
        path = abspath(path)
        temp_songs: list = self.library.copy()
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

    def scan_folders(self: ClassVar) -> None:
        try:
            if self.settings['scan_subfolders']:
                folders: list = self.settings['folders'].copy()
                for folder in folders:
                    if exists(folder):
                        for file in listdir(folder):
                            if file.endswith(('.mp3', '.flac', '.ogg')) and file not in self.library:
                                self.library.append(abspath(join(folder, file)))              
                            elif isdir(join(folder, file)) and file not in ('System Volume Information', '$RECYCLE.BIN') and file not in folders:
                                folders.append(abspath(join(folder, file)))
            else:
                for folder in self.settings['folders']:
                    if exists(folder):
                        for file in listdir(folder):
                            if file.endswith(('.mp3', '.flac', '.ogg')) and file not in self.library:
                                self.library.append(abspath(join(folder, file)))
            # add songs to cache
            for song in self.library:
                if not song in self.songs_cache:
                    self.new_song(song)
            # add songs to list
            self.songs = self.library.copy() if self.playlist == 'Library' else self.settings['playlists'][self.playlist]['Songs']
        except Exception as err_obj:
            self.log(err_obj)

    def change_theme(self: ClassVar) -> None:
        try:
            theme: str = self.theme.get()
            if theme == 'System':
                self.settings['use_system_theme'] = True
            else:
                self.settings['use_system_theme'] = False
                self.settings['theme'] = theme
        except Exception as err_obj:
            self.log(err_obj)

    def change_updates(self: ClassVar) -> None:
            self.settings['updates'] = self.updates.get()

    def change_acceleration(self: ClassVar, _: Event) -> None:
        self.settings['wheel_acceleration'] = round(self.wheel_acceleration.get(), 0)

    def change_subfolders(self: ClassVar) -> None:
        self.settings['scan_subfolders'] = self.scan_subfolders.get()
        Thread(target=self.scan_folders, daemon=True).start()

    def change_buffer(self: ClassVar) -> None:
        self.settings['buffer'] = self.buffer.get()

    def check_update(self: ClassVar) -> None:
        try:
            server_version: str = get('https://raw.githubusercontent.com/losek1/Sounder5/master/updates/version.txt').text
            if server_version != self.version[0] and int(server_version.replace('.', '')) > int(self.version[0].replace('.', '')):
                self.toaster.show_toast(f'Update {server_version} is available', 'If you don\'t want to see this message go to settings and disable automatic updates!', threaded=True, icon_path='Resources\\Icons\\Updater\\setup.ico')
                self.update_panel.lift()
        except Exception as err_obj:
            self.log(err_obj)

    def do_update(self: ClassVar) -> None:
        if isfile('Updater.exe'):
            startfile(f'Updater.exe {self.version[0]}')
            self.exit_app()

    def snooze_update(self: ClassVar) -> None:
        self.update_panel.lower()
        self.after(300000, lambda: self.update_panel.lift())

    def change_playback(self: ClassVar) -> None:
        self.settings['start_playback'] = self.start_playback.get()

    def change_sort(self: ClassVar) -> None:
        self.settings['sort_by'] = self.sort_by.get()
        if self.playlist == 'Library':
            self.sort_panels(self.get_filtered_search(), self.library, True)
        else:
            self.sort_panels('', self.settings['playlists'][self.playlist]['Songs'], True)

    def update_thread(self: ClassVar) -> None:
        Thread(target=self.check_update, daemon=True).start()

    def open_search(self: ClassVar) -> None:
        entry_content: str = self.lib_entry.get()
        if entry_content:
            self.search()
        else:
            if self.lib_entry.winfo_ismapped():
                self.lib_entry.pack_forget()
                self.lib_search.config(style='second.TButton')
                self.focus_set()
            else:
                self.lib_entry.pack(side='right', anchor='c')
                self.lib_search.config(style='third.TButton')
                self.lib_entry.focus_set()

    def get_filtered_search(self: ClassVar) -> str:
        allowed_chars: str = 'abcdefghijklmnopqrstuvwxyz123456789. '
        entry_content: str = self.lib_entry.get().lower()
        clean_content: str = ''
        for letter in entry_content:
            if letter in allowed_chars: clean_content += letter
        return clean_content

    def search(self: ClassVar, _: Event=None) -> None:
        self.sort_panels(self.get_filtered_search(), self.library)
        self.player_canvas.yview_moveto(0)

    def sort_panels(self: ClassVar, search_word: str, songs: list, refresh_panels: bool = False) -> None:
        temp_songs: list = []
        # apply search
        if search_word:
            for song in songs:
                result = f'{self.songs_cache[song]["title"]} {self.songs_cache[song]["artist"]} {self.songs_cache[song]["album"]} {song}'
                if findall(search_word, result.lower()) or compare(search_word, self.songs_cache[song]['title'], 2) or compare(search_word, self.songs_cache[song]['artist'], 3) or compare(search_word, self.songs_cache[song]['album'], 3):
                    temp_songs.append(song)
        else:
            temp_songs = songs.copy()
        # apply sort
        if self.settings['sort_by'] == 'A-Z':
            temp_songs.sort(key=self.sort_songs)
        elif self.settings['sort_by'] == 'Z-A':
            temp_songs.sort(key=self.sort_songs, reverse=True)
        if not temp_songs:
            self.search_panel.pack(side='top', fill='x', pady=5, padx=10)
        else:
            self.search_panel.pack_forget()
        # apply search
        if self.playlist == 'Library': self.songs = temp_songs.copy()
        # apply shuffle
        if self.songs and self.settings['shuffle']: shuffle(self.songs)
        # forget panels
        if refresh_panels:
            for song in self.library:
                if song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped():
                    self.song_panels[song].pack_forget()
        else:
            for song in list(set(temp_songs)^set(songs)):
                if song in self.library and song in self.song_panels and self.song_panels[song].winfo_ismapped():
                    self.song_panels[song].pack_forget()
        # pack panels
        for song in temp_songs:
            if song in self.library and song in self.song_panels and not self.song_panels[song].winfo_ismapped():
                self.song_panels[song].pack(side='top', fill='x', pady=5, padx=10)

    def sort_songs(self: ClassVar, song: str) -> str:
        if song in self.songs_cache:
            return self.songs_cache[song]['title'][:2].lower()
        else:
            return ''

    def toggle_shuffle(self: ClassVar) -> None:
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

    def cache_song(self: ClassVar, song: str) -> None:
        album_art: ClassVar = self.icons['note']
        song_title: str = splitext(basename(song))[0]
        song_artist: str = 'Unknown'
        album: str = 'Unknown'
        song_metadata: ClassVar = None
        if song.endswith('.mp3'):
            song_metadata: ClassVar = MP3(song)
            if 'TIT2' in song_metadata:
                song_title = f'{song_metadata["TIT2"]}'
            if 'TPE1' in song_metadata:
                song_artist = f'{song_metadata["TPE1"]}'
            if 'TALB' in song_metadata:
                album = f'{song_metadata["TALB"]}'
            if 'APIC:' in song_metadata:
                album_art = ImageTk.PhotoImage(Image.open(BytesIO(song_metadata.get('APIC:').data)).resize((25, 25)))
        elif song.endswith('.flac'):
            song_metadata: ClassVar = FLAC(song)
            if 'title' in song_metadata:
                song_title = song_title.join(song_metadata['title'])
            if 'artist' in song_metadata:
                song_artist = song_artist.join(song_metadata['artist'])
            if 'album' in song_metadata:
                album = album.join(song_metadata['album'])
            if song_metadata.pictures:
                album_art = ImageTk.PhotoImage(Image.open(BytesIO(song_metadata.pictures[0].data)).resize((25, 25)))
        elif song.endswith('.ogg'):
            song_metadata: ClassVar = OggVorbis(song)
            if 'title' in song_metadata:
                song_title = song_title.join(song_metadata['title'])
            if 'comment' in song_metadata:
                song_artist = song_artist.join(song_metadata['comment'])
        # cache data
        self.songs_cache[song]: dict =  {'title': song_title, 'artist': song_artist, 'album': album, 'album_art': album_art, 'length': song_metadata.info.length}

    def new_song(self: ClassVar, song: str) -> None:
        self.cache_song(song)
        self.add_song(song)

    def add_song(self: ClassVar, song: str) -> None:
        try:
            self.song_panels[song]: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
            ttk.Label(self.song_panels[song], image=self.songs_cache[song]['album_art']).pack(side='left', anchor='c', pady=10, padx=10)
            info_frame: ClassVar = ttk.Frame(self.song_panels[song], style='second.TFrame')
            ttk.Label(info_frame, text=f'{self.songs_cache[song]["title"]}', style='fifth.TLabel').place(x=5, y=5)
            ttk.Label(info_frame, text=f'{self.songs_cache[song]["artist"]}', style='sixth.TLabel').place(x=5, y=28)
            info_frame.pack(side='left', fill='both', expand=True)
            ttk.Button(self.song_panels[song], image=self.icons['menu'], command=lambda: self.song_menu.show(song)).pack(side='right', anchor='c', fill='y', pady=10, padx=(0, 5))
            self.songs_cache[song]['play_pause']: ClassVar = ttk.Button(self.song_panels[song], image=self.icons['play_pause'][0], command=lambda: self.panel_play(song))
            self.songs_cache[song]['play_pause'].pack(side='right', anchor='c', fill='y', pady=10, padx=(0, 5))
            self.songs_cache[song]['heart']: ClassVar = ttk.Button(self.song_panels[song], image=self.icons['heart'][song in self.settings['playlists']['Favorites']['Songs']], command=lambda: self.favorites_song(song))
            self.songs_cache[song]['heart'].pack(side='right', anchor='c', fill='y', pady=10, padx=5)
        except Exception as err_obj:
            self.log(err_obj)

    def remove_song(self: ClassVar, song: str) -> None:
        try:
            if song in self.song_panels and song in self.library:
                self.song_panels[song].destroy()
                del self.song_panels[song], self.songs_cache[song]
                self.library.remove(song)
                if song in self.songs: self.songs.remove(song)
        except Exception as err_obj:
            self.log(err_obj)

    def favorites_song(self: ClassVar, song: str) -> None:
        if song in self.settings['playlists']['Favorites']['Songs']:
            self.songs_cache[song]['heart'].configure(image=self.icons['heart'][0])
            self.settings['playlists']['Favorites']['Songs'].remove(song)
        else:
            self.songs_cache[song]['heart'].configure(image=self.icons['heart'][1])
            self.settings['playlists']['Favorites']['Songs'].append(song)

    def update_active_panel(self: ClassVar, song: str) -> None:
        for active_song in self.active_panels:
            if active_song in self.songs_cache:
                self.songs_cache[active_song]['play_pause'].configure(image=self.icons['play_pause'][0])
                self.active_panels.remove(active_song)
        if song in self.songs_cache and not self.paused and mixer.music.get_busy():
            self.songs_cache[song]['play_pause'].configure(image=self.icons['play_pause'][1])
            self.active_panels.append(song)

    def update_play_pause(self: ClassVar) -> None:
        self.play_button.configure(image=self.icons['play_pause'][not self.paused and mixer.music.get_busy()])

    def update_info_panel(self: ClassVar, song: str) -> None:
        max_length: int = int(self.song_album.master.winfo_width() / 10) + 1
        if song in self.songs_cache:
            self.song_album.configure(image=self.songs_cache[song]['album_art'])
            if len(self.songs_cache[song]['title']) > max_length:
                self.song_title.configure(text=f'{self.songs_cache[song]["title"][:max_length - 3]}...')
            else:
                self.song_title.configure(text=self.songs_cache[song]['title'])
            self.song_artist.configure(text=self.songs_cache[song]['artist'])
            
    def update_title_length(self: ClassVar, _: Event) -> None:
        if self.song in self.songs_cache:
            max_length: int = int(self.song_album.master.winfo_width() / 10) + 4
            if len(self.songs_cache[self.song]['title']) > max_length:
                self.song_title.configure(text=f'{self.songs_cache[self.song]["title"][:max_length - 3]}...')
            else:
                self.song_title.configure(text=self.songs_cache[self.song]['title'])

    def update_progress_info(self: ClassVar, song: str) -> None:
        minute: float = 0.0; second: float = 0.0
        minute, second = divmod(self.songs_cache[song]['length'], 60)
        self.time_passed['text'] = '0:00'
        self.song_length['text'] = f'{int(minute)}:{str(int(second)).zfill(2)}'
        self.progress_bar.configure(value=0, maximum=self.songs_cache[song]['length'])

    def target_playlist(self: ClassVar) -> None:
        self.playlist = self.menu_playlist.get()
        self.songs = self.library.copy() if self.playlist == 'Library' else self.settings['playlists'][self.playlist]['Songs']
        if self.songs and self.settings['shuffle']: shuffle(self.songs)
        if not self.paused and not mixer.music.get_busy():
            self.button_play()

    def init_mixer(self: ClassVar) -> None:
        try:
            size: int = 1024
            if self.settings['buffer'] == 'Slow': size = 2048
            if self.settings['buffer'] == 'Fast': size = 512
            mixer.pre_init(44800, -16, 2, size)
            mixer.init()
        except Exception as err_obj:
            self.log(err_obj)

    def mixer_play(self: ClassVar, song: str) -> None:
        try:
            if exists(song):
                mixer.music.load(song)
                mixer.music.play()
                self.paused = False
                self.song = self.settings['last_song'] = song
                self.update_progress_info(song)
                self.update_active_panel(song)
                self.update_info_panel(song)
                self.update_play_pause()
                if not self.mixer_active:
                    self.mixer_thread()
            else:
                self.remove_song(song)
        except Exception as err_obj:
            self.log(err_obj)

    def mixer_pause(self: ClassVar) -> None:
        mixer.music.pause()
        self.paused = True
        self.update_active_panel(self.song)
        self.update_play_pause()

    def mixer_unpause(self: ClassVar) -> None:
        mixer.music.unpause()
        self.paused = False
        self.update_active_panel(self.song)
        self.update_play_pause()

    def panel_play(self: ClassVar, song: str) -> None:
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
                    self.songs = self.settings['playlists'][self.playlist]['Songs'].copy()
                if self.songs and self.settings['shuffle']: shuffle(self.songs)
            self.mixer_play(song)

    def button_play(self: ClassVar) -> None:
        if self.song and self.paused:
            self.mixer_unpause()
        elif self.song and not self.paused and mixer.music.get_busy():
            self.mixer_pause()
        elif self.song in self.songs:
            self.mixer_play(self.song)
        elif self.songs:
            self.mixer_play(self.songs[0])
        else:
            self.songs = self.library.copy() if self.playlist == 'Library' else self.settings['playlists'][self.playlist]['Songs']
            if self.songs and self.settings['shuffle']: shuffle(self.songs)
            self.mixer_play(self.songs[0])

    def mixer_thread(self: ClassVar) -> None:
        self.mixer_active = True
        if mixer.music.get_busy() and self.song:
            position: float = mixer.music.get_pos() / 1000
            self.progress_bar['value'] = position
            self.time_passed['text'] = f'{int(divmod(position, 60)[0])}:{str(int(divmod(position, 60)[1])).zfill(2)}'
            self.after(150, self.mixer_thread)
        elif not mixer.music.get_busy():
            self.mixer_active = False
            self.mixer_after()

    def mixer_after(self: ClassVar) -> None:
        self.song_length['text'] = self.time_passed['text']
        self.update_active_panel('')
        self.update_play_pause()
        if self.settings['repeat'] == 'One':
            self.after(100, self.button_play)
        elif self.settings['repeat'] == 'All':
            self.after(100, self.button_next)

    def button_next(self: ClassVar) -> None:
        if self.song in self.songs:
            new_index: int = self.songs.index(self.song) + 1
            self.song = self.songs[new_index if new_index < len(self.songs) else 0]
            self.mixer_play(self.song)
        elif self.songs:
            self.song = self.songs[0]
            self.mixer_play(self.song)

    def button_previous(self: ClassVar) -> None:
        if self.song in self.songs:
            new_index: int = self.songs.index(self.song) - 1
            self.song = self.songs[new_index if new_index >= 0 else -1]
            self.mixer_play(self.song)
        elif self.songs:
            self.song = self.songs[-1]
            self.mixer_play(self.song)

    def toggle_volume(self: ClassVar) -> None:
        if self.muted:
            self.set_volume(self.settings['volume'])
            self.muted = False
        else:
            mixer.music.set_volume(0.0)
            self.muted = True
            self.mute_button.configure(image=self.icons['speaker'][0])

    def set_volume(self: ClassVar, volume: str) -> None:
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
        if self.muted: self.muted = False

    def toggle_repeat(self: ClassVar) -> None:
        if self.settings['repeat'] == 'None':
            self.settings['repeat'] = 'All'
            self.repeat_button.configure(image=self.icons['repeat'][0], style='second.TButton')
        elif self.settings['repeat'] == 'All':
            self.repeat_button.configure(image=self.icons['repeat'][1])
            self.settings['repeat'] = 'One'
        else:
            self.settings['repeat'] = 'None'
            self.repeat_button.configure(style='TButton', image=self.icons['repeat'][0])


if __name__ == '__main__':
    Sounder().mainloop()
    

    