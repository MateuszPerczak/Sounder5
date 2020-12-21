try:
    from typing import ClassVar
    from tkinter import Tk, ttk, StringVar, BooleanVar, DoubleVar, Canvas, Event
    from tkinter.filedialog import askdirectory
    from tkinter.messagebox import askyesno
    from os.path import isfile, join, isdir, basename, abspath, join
    from os import startfile, listdir # getcwd, listdir, startfile, remove
    from json import load, dump
    from json.decoder import JSONDecodeError
    from logging import basicConfig, error, ERROR, getLevelName, getLogger, shutdown
    from traceback import format_exc
    from PIL import Image, ImageTk
    from random import choices
    from string import ascii_uppercase, digits
    from Components.SystemTheme import get_theme
    from Components.Debugger import Debugger
    from requests import get
    from threading import Thread
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
        basicConfig(filename='errors.log', level=ERROR)

    def log(self: ClassVar, err_obj: ClassVar) -> None:
        # log error to file
        error(err_obj, exc_info=True)
        self.error_label['text'] = format_exc().split("\n")[-2]
        self.error_panel.lift()

    def init_settings(self: ClassVar) -> None:
        try:
            # variables
            default_settings: dict = {'wheel_acceleration': 1.0, 'updates': True, 'folders': [], 'use_system_theme': True, 'theme': 'Light', 'page': 'Library', 'playlists': {'Favorites': {'Name': 'Favorites', 'Songs': []}}}
            self.settings: dict = {}
            self.version: tuple = ('0.4.0', '211220')
            # load settings
            if isfile('Resources\\Settings\\Settings.json'):
                with open('Resources\\Settings\\Settings.json', 'r') as data:
                    try:
                        self.settings = load(data)
                    except JSONDecodeError as err_obj:
                        self.settings = default_settings
            else:
                self.settings = default_settings
                self.save_settings()
            # verify settings
            for key in default_settings:
                self.settings[key] =  self.settings.get(key, default_settings[key])
            del default_settings
        except Exception as err_obj:
            self.log(err_obj)

    def apply_settings(self: ClassVar) -> None:
        # check theme
        if self.settings['use_system_theme']:
            self.settings['theme']: str = get_theme()
        # check for updates
        if self.settings['updates']:
            self.after(5000, self.update_thread)

    def save_settings(self: ClassVar) -> None:
        # save last page
        self.settings['page'] = self.menu_option.get()
        try:
            with open('Resources\\Settings\\Settings.json', 'w') as data:
                dump(self.settings, data)
        except Exception as err_obj:
            self.log(err_obj)

    def restore_default(self: ClassVar) -> None:
        if askyesno('Restore default configuration', 'Are you sure you want to restore the default configuration?', icon='warning'):
            self.settings: dict = {}
            self.save_settings()
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
        self.layout.configure('second.TLabel', background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3], font=('catamaran 20 bold'))
        self.layout.configure('third.TLabel', background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3])
        self.layout.configure('fourth.TLabel', background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3], font=('catamaran 16 bold'))
        self.layout.configure('sixth.TLabel', background=theme[self.settings['theme']][1], foreground=theme[self.settings['theme']][3])
        # radiobutton
        self.layout.configure('TRadiobutton', background=theme[self.settings['theme']][0], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w', padding=5, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('second.TRadiobutton', anchor='c', padding=5, width=6)
        self.layout.configure('third.TRadiobutton', anchor='c', padding=5, width=8)

        # button
        self.layout.configure('TButton', background=theme[self.settings['theme']][0], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w')
        self.layout.map('TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][1]), ('selected', theme[self.settings['theme']][1])])
        self.layout.configure('second.TButton', background=theme[self.settings['theme']][1], relief='flat', font=('catamaran 13 bold'), foreground=theme[self.settings['theme']][3], anchor='w')
        self.layout.map('second.TButton', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('active', theme[self.settings['theme']][0]), ('selected', theme[self.settings['theme']][0])])
        self.layout.configure('second.TButton', anchor='c')
        self.layout.configure('third.TButton', anchor='c')
        # scrollbar
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background=theme[self.settings['theme']][1], darkcolor=theme[self.settings['theme']][1], lightcolor=theme[self.settings['theme']][1], troughcolor=theme[self.settings['theme']][1], bordercolor=theme[self.settings['theme']][1])
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', theme[self.settings['theme']][0]), ('disabled', theme[self.settings['theme']][1]), ('active', theme[self.settings['theme']][0]), ('!active', theme[self.settings['theme']][0])])   
        # scale
        self.layout.map('Horizontal.TScale', background=[('pressed', '!disabled', theme[self.settings['theme']][2]), ('active', theme[self.settings['theme']][2])])
        # self.layout.configure('Horizontal.TScale', troughcolor='#151515', background='#333', relief="flat", gripcount=0, darkcolor="#151515", lightcolor="#151515", bordercolor='#151515')
        self.layout.configure('Horizontal.TScale', troughcolor=theme[self.settings['theme']][0], background=theme[self.settings['theme']][1], relief='flat', gripcount=0, darkcolor=theme[self.settings['theme']][0], lightcolor=theme[self.settings['theme']][0], bordercolor=theme[self.settings['theme']][0])
        # entry
        self.layout.configure('TEntry', background=theme[self.settings['theme']][1],  foreground=theme[self.settings['theme']][3], fieldbackground=theme[self.settings['theme']][0], selectforeground=theme[self.settings['theme']][3], selectbackground=theme[self.settings['theme']][2], font=('catamaran 20 bold'))
        self.layout.map('TEntry', foreground=[('active', '!disabled', 'disabled', theme[self.settings['theme']][3])])   
        del theme

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
            'play_pause': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\play.png').resize((35, 35))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\pause.png').resize((35, 35)))),
            'next': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\next.png').resize((35, 35))),
            'previous': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\previous.png').resize((35, 35))),
            'repeat': (ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\repeat.png').resize((25, 25))), ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\repeat_one.png').resize((25, 25)))),
            'shuffle': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\shuffle.png').resize((25, 25))),
            'muted': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\muted.png').resize((25, 25))),
            'edit': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\edit.png').resize((25, 25))),
            'menu': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\menu.png').resize((25, 25))),
            'clock': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\clock.png').resize((25, 25))),
            'note': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\note.png').resize((25, 25))),
            'back': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\back.png').resize((25, 25))),
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
            'cache': ImageTk.PhotoImage(Image.open(f'Resources\\Icons\\{self.settings["theme"]}\\cache.png').resize((25, 25))),

            }
        self.iconphoto(False, self.icons['logo'])

    def init_ui(self: ClassVar) -> None:
        # variables
        self.menu_option: StringVar = StringVar(value=self.settings['page'])
        self.menu_playlist: StringVar = StringVar(value=self.settings['page'])
        self.last_panel: str = ''
        self.folder_panels: dict = {}
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
        # player panel
        self.player_panel: ClassVar = ttk.Frame(self)
        # top panel
        player_top_panel: ClassVar = ttk.Frame(self.player_panel)
        # menu panel 
        self.menu_panel: ClassVar = ttk.Frame(player_top_panel, style='second.TFrame')
        ttk.Radiobutton(self.menu_panel, image=self.icons['library'], text='Library', compound='left', value='Library', style='menu.TRadiobutton', variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=(10, 0))
        ttk.Radiobutton(self.menu_panel, image=self.icons['folder'][1], text='Folders', compound='left', value='Folders', style='menu.TRadiobutton', variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=(10, 0))
        ttk.Radiobutton(self.menu_panel, image=self.icons['settings'], text='Settings', compound='left', value='Settings', style='menu.TRadiobutton', variable=self.menu_option, command=self.show_panel).pack(side='top', fill='x', padx=10, pady=10)
        ttk.Label(self.menu_panel, text='Playlists', style='menu.TLabel').pack(side='top', fill='x', padx=10)
        ttk.Button(self.menu_panel, image=self.icons['plus'], text='Add playlist', compound='left', command=self.add_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
        ttk.Radiobutton(self.menu_panel, image=self.icons['heart'][1], text='Favorites', compound='left', value='Favorites', style='menu.TRadiobutton', variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
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
        # playlist panel
        self.playlist_panel: ClassVar = ttk.Frame(player_options_panel)
        # playlist arbitrary name
        self.playlist_an: ClassVar = ttk.Label(self.playlist_panel, image=None, text='', style='fourth.TLabel', compound='left')
        self.playlist_an.pack(side='left', anchor='c', padx=(10, 0))
        self.playlist_an.bind('<Double-Button-1>', lambda _: self.playlist_options.lift())
        # playlist menu button
        ttk.Button(self.playlist_panel, image=self.icons['menu'], style='second.TButton', command=lambda: self.playlist_options.lift()).pack(side='right', anchor='c', padx=(10, 0))
        # playlist number of songs 
        self.playlist_nos: ClassVar = ttk.Label(self.playlist_panel, image=self.icons['note'], text='Songs 0', style='sixth.TLabel', compound='left')
        self.playlist_nos.pack(side='right', anchor='c', padx=(10, 0))
        # playlist total time
        self.playlist_tt: ClassVar = ttk.Label(self.playlist_panel, image=self.icons['clock'], text='00:00:00', style='sixth.TLabel', compound='left')
        self.playlist_tt.pack(side='right', anchor='c', padx=(10, 0))
        self.playlist_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # playlist options
        self.playlist_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.playlist_options, image=self.icons['edit'], style='sixth.TLabel').pack(side='left', anchor='c', padx=(10, 1))
        # playlist entry
        self.playlist_entry: ClassVar = ttk.Entry(self.playlist_options, exportselection=False, font=('catamaran 16 bold'))
        self.playlist_entry.pack(side='left', anchor='c')
        self.playlist_entry.bind('<Return>', self.rename_playlist)
        ttk.Button(self.playlist_options, image=self.icons['back'], style='second.TButton', command=lambda: self.playlist_panel.lift()).pack(side='right', anchor='c', padx=(10, 0))
        self.playlist_remove: ClassVar = ttk.Button(self.playlist_options, text='Remove playlist', image=self.icons['delete'], compound='left', style='second.TButton', command=self.remove_playlist)
        self.playlist_remove.pack(side='right', anchor='c', padx=(10, 0))
        self.playlist_options.place(x=0, y=0, relwidth=1, relheight=1)
        # folder options
        self.folder_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.folder_options, image=self.icons['folder'][1], text='Folders', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.folder_options, image=self.icons['plus'], text='Add folder', compound='left', style='second.TButton', command=self.new_folder).pack(side='right', anchor='c', padx=(10, 0))
        self.folder_options.place(x=0, y=0, relwidth=1, relheight=1)
        # settings options
        self.settings_options: ClassVar = ttk.Frame(player_options_panel)
        ttk.Label(self.settings_options, image=self.icons['settings'], text='Settings', style='fourth.TLabel', compound='left').pack(side='left', anchor='c', padx=(10, 0))
        ttk.Button(self.settings_options, image=self.icons['restore'], text='Restore default', compound='left', style='second.TButton', command=self.restore_default).pack(side='right', anchor='c', padx=(10, 0))
        ttk.Button(self.settings_options, image=self.icons['checkmark'], text='Apply', compound='left', style='second.TButton', command=self.save_settings).pack(side='right', anchor='c', padx=(10, 0))
        self.settings_options.place(x=0, y=0, relwidth=1, relheight=1)
        # library options
        self.library_options: ClassVar = ttk.Frame(player_options_panel)


        self.library_options.place(x=0, y=0, relwidth=1, relheight=1)

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
            self.add_folder(folder)
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
        ttk.Scale(settings_acceleration, variable=self.wheel_acceleration, from_=0, to=8, command=self.change_acceleration).pack(side='right', anchor='c', fill='x', ipadx=20)
        ttk.Label(settings_acceleration, text='Slow').pack(side='right', anchor='c', fill='y', pady=10, padx=10)
        # cache
        settings_cache: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
        cache_panel: ClassVar = ttk.Frame(settings_cache, style='second.TFrame')
        ttk.Label(cache_panel, image=self.icons['cache'], text='Music cache mode', compound='left').pack(side='left', anchor='c', fill='y')
        ttk.Radiobutton(cache_panel, text='Dynamic', style='third.TRadiobutton', value='Dynamic').pack(side='right', anchor='c')
        ttk.Radiobutton(cache_panel, text='Static', style='third.TRadiobutton', value='Static').pack(side='right', anchor='c', padx=(10, 10))
        cache_panel.pack(side='top', fill='x', pady=10, padx=10)
        ttk.Label(settings_cache, image=self.icons['info'], text='Note: We recommend using \'Dynamic\' mode for best performance!', compound='left').pack(side='top', fill='x', padx=10, pady=(0, 10))
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
        # update variable
        self.settings_panels = (settings_acceleration, settings_theme, settings_updates, settings_cache, settings_about)
        # bottom panel
        player_bot_panel: ClassVar = ttk.Frame(self.player_panel, style='second.TFrame')
        # buttons, song name, etc ...
        center_panel: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        self.play_button: ClassVar = ttk.Button(center_panel, image=self.icons['play_pause'][0], takefocus=False)
        self.play_button.place(relx=0.5, rely=0.5, anchor='center')
        # next button
        ttk.Button(center_panel, image=self.icons['next'], takefocus=False).place(relx=0.7, rely=0.5, anchor='center')
        # previous button
        ttk.Button(center_panel, image=self.icons['previous'], takefocus=False).place(relx=0.3, rely=0.5, anchor='center')
        # shuffle button
        self.shuffle_button: ClassVar = ttk.Button(center_panel, image=self.icons['shuffle'], takefocus=False)
        self.shuffle_button.place(relx=0.1, rely=0.5, anchor='center')
        # repeat button
        self.repeat_button: ClassVar = ttk.Button(center_panel, image=self.icons['repeat'][0], takefocus=False)
        self.repeat_button.place(relx=0.9, rely=0.5, anchor='center')
        center_panel.place(relx=0.5, y=10, width=350, height=48, anchor='n')
        volume_panel: ClassVar = ttk.Frame(player_bot_panel, style='second.TFrame')
        # mute button
        self.mute_button: ClassVar = ttk.Button(volume_panel, image=self.icons['muted'], takefocus=False, command=None)
        self.mute_button.pack(side='left', anchor='center', padx=5)
        # volume bar
        self.volume_bar: ClassVar = ttk.Scale(volume_panel, orient='horizontal', from_=0, to=1, command=None)
        self.volume_bar.pack(side='left', anchor='center', padx=5, fill='x', expand=True)
        volume_panel.place(relx=1, y=10, relwidth=0.22, height=48, anchor='ne')
        player_bot_panel.pack(side='top', fill='x', ipady=45)

        self.player_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # error panel
        self.error_panel: ClassVar = ttk.Frame(self)
        error_content: ClassVar = ttk.Frame(self.error_panel)
        ttk.Label(error_content, image=self.icons['error'], text='Something went wrong', compound='top', style='second.TLabel').pack(side='top')
        self.error_label: ClassVar = ttk.Label(error_content, text='We are unable to display the error message', style='third.TLabel')
        self.error_label.pack(side='top')
        ttk.Button(error_content, text='OK', style='third.TButton', command=self.exit_app).pack(side='top', pady=(50, 0), padx=10)
        ttk.Button(error_content, text='Open Logs', style='third.TButton', command=self.open_logs).pack(side='top', pady=(10, 0), padx=10)
        ttk.Label(self.error_panel, text=f'version: {self.version[0]} [build: {self.version[1]}]', style='third.TLabel').pack(side='bottom', anchor='w', padx=10, pady=5)
        error_content.place(relx=.5, rely=.5, anchor='c')
        self.error_panel.place(x=0, y=0, relwidth=1, relheight=1)
        
    def init_player(self: ClassVar) -> None:
        # variables
        self.songs: list = []
        # scan folders
        self.scan_folders()
        # show last panels
        self.player_panel.lift()
        self.show_panel()
        # bind scroll to content
        self.bind('<MouseWheel>', self.on_wheel)

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
            # pack
            if panel == 'Folders':
                for folder in self.folder_panels:
                    if not self.folder_panels[folder].winfo_ismapped():
                        self.folder_panels[folder].pack(side='top', fill='both', expand=True, pady=5, padx=10)
            if panel == 'Settings':
                for setting in self.settings_panels:
                    if not setting.winfo_ismapped():
                        setting.pack(side='top', fill='x', pady=5, padx=10)
        self.last_panel = panel

    def open_logs(self: ClassVar) -> None:
        if isfile("errors.log"): startfile("errors.log")

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
            self.playlist_nos['text'] = f'Songs {len(self.settings["playlists"][selected_playlist]["Songs"])}'
            # update entry
            self.playlist_entry.state(['!disabled'])
            self.playlist_entry.delete(0, 'end')
            self.playlist_entry.insert(0, self.settings['playlists'][selected_playlist]['Name'])
            # change icon acording to playlist type and disable some buttons
            if selected_playlist == 'Favorites':
                self.playlist_an['image'] = self.icons['heart'][1]
                self.playlist_remove.state(['disabled'])
                self.playlist_entry.state(['disabled'])
            else:
                self.playlist_an['image'] = self.icons['playlist']
                self.playlist_remove.state(['!disabled'])
        del selected_playlist

    def add_playlist(self: ClassVar) -> None:
        playlist_id: str = ''.join(choices(ascii_uppercase + digits, k=4))
        if not playlist_id in self.settings['playlists']:
            self.settings['playlists'][playlist_id]: dict = {'Name': f'Playlist {len(self.settings["playlists"])}', 'Songs': []}
            ttk.Radiobutton(self.menu_panel, image=self.icons['playlist'], text=self.settings['playlists'][playlist_id]['Name'], compound='left', value=playlist_id, style='menu.TRadiobutton', variable=self.menu_playlist, command=self.show_playlist).pack(side='top', fill='x', padx=10, pady=(10, 0))
        del playlist_id
        
    def remove_playlist(self):
        try:
            if askyesno('Remove playlist', 'Are you sure you want to remove this playlist?\nThis cannot be undone!', icon='warning'):
                selected_playlist: str = self.menu_playlist.get()
                playlist_list: list = list(self.settings['playlists'].keys())
                if selected_playlist in self.settings['playlists'] and not selected_playlist == 'Favorites':
                    playlist_list.remove(selected_playlist)
                    # selects last playlist
                    self.menu_playlist.set(playlist_list[len(playlist_list) - 1])
                    self.show_playlist()
                    # removes playlist button
                    self.get_playlist_button(selected_playlist).destroy()
                    del self.settings['playlists'][selected_playlist]
                del selected_playlist, playlist_list
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
                self.playlist_panel.lift()
            else:
                print('error while renaming playlist')
            self.update_playlist(selected_playlist)
            del new_name, selected_playlist
        except Exception as err_obj:
            self.log(err_obj)

    def new_folder(self: ClassVar) -> None:
        new_dir: str = askdirectory()
        if new_dir and new_dir not in self.settings['folders']:
            self.settings['folders'].append(new_dir)
            self.add_folder(new_dir)
            self.folder_panels[new_dir].pack(side='top', fill='both', expand=True, pady=5, padx=10)
        del new_dir

    def add_folder(self: ClassVar, path: str) -> None:
        try:
            self.folder_panels[path]: ClassVar = ttk.Frame(self.player_content, style='second.TFrame')
            path_label: ClassVar = ttk.Label(self.folder_panels[path], image=self.icons['folder'][0], text=basename(path), compound='left')
            path_label.pack(side='left', anchor='c', fill='y', pady=10, padx=10)
            ttk.Button(self.folder_panels[path], image=self.icons['delete'], takefocus=False, command=lambda: self.remove_folder(path)).pack(side='right', padx=10, anchor='c')
            self.folder_panels[path].bind('<Leave>', lambda _:path_label.configure(text=basename(path)))
            self.folder_panels[path].bind('<Enter>', lambda _:path_label.configure(text=path))
        except Exception as err_obj:
            self.dump(err_obj)

    def remove_folder(self: ClassVar, path: str) -> None:
        if askyesno('Remove folder', 'Are you sure you want to remove this folder?', icon='warning') and path in self.settings['folders']:
            self.folder_panels[path].destroy()
            self.settings['folders'].remove(path)
            del self.folder_panels[path]

    def scan_folders(self: ClassVar) -> None:
        for folder in self.settings['folders']:
            for file in listdir(folder):
                if file.endswith(('.mp3', '.flac', '.wav', '.ogg')) and file not in self.songs:
                    self.songs.append(abspath(join(folder, file)))


    def change_theme(self: ClassVar) -> None:
        try:
            theme: str = self.theme.get()
            if theme == 'System':
                self.settings['use_system_theme'] = True
            else:
                self.settings['use_system_theme'] = False
                self.settings['theme'] = theme
            del theme
        except Exception as err_obj:
            self.dump(err_obj)

    def change_updates(self: ClassVar) -> None:
            self.settings['updates'] = self.updates.get()

    def change_acceleration(self: ClassVar, _: Event) -> None:
        self.settings['wheel_acceleration'] = round(self.wheel_acceleration.get(), 0)

    def check_update(self: ClassVar) -> None:
        server_version: str = get('https://raw.githubusercontent.com/losek1/Sounder4/master/updates/version.txt').text
        print(server_version)
        # if int(self.VERSION.replace('.', '')) < int(server_version.replace('.', '')):
        #     pass
    '''
    Todo:
    +add proper version checking and build checking for update
    +add custom messages
    +add a function that disables music playback when critical
    + add a check for file size when adding songs
    '''


    def update_thread(self: ClassVar) -> None:
        Thread(target=self.check_update, daemon=True).start()

if __name__ == '__main__':
    Sounder().mainloop()

    