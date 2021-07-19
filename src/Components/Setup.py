try:
    from tkinter import Toplevel, ttk, Canvas, StringVar, BooleanVar, PhotoImage
    from tkinter.filedialog import askdirectory, askopenfilename
    from os.path import basename, abspath
    from time import sleep
    from threading import Thread
    from json import load
    from json.decoder import JSONDecodeError
except ImportError as err:
    exit(err)


class SSetup(Toplevel):
    def __init__(self, parent, settings: dict) -> None:
        super().__init__(parent)
        # variables
        self.settings = settings
        self.parent = parent
        self.pages: int = 5
        # hide window
        self.withdraw()
        # configure window
        self.geometry(f'500x620+{int(self.winfo_x() + ((self.winfo_screenwidth() / 2) - 250))}+{int(self.winfo_y() + ((self.winfo_screenheight() / 2) - 310))}')
        self.resizable(False, False)
        self.title('Sounder configurator')
        self.protocol('WM_DELETE_WINDOW', self.exit_app)
        # init layout
        self.init_layout()
        # load icons
        self.load_icons()
        # apply theme
        self.apply_theme()
        # init ui
        self.init_ui()
        # show window
        self.deiconify()

    def exit_app(self) -> None:
        self.quit()
        self.destroy()
        
    def init_layout(self) -> None:
        # init theme object
        self.layout: ttk.Style = ttk.Style()
        # set theme to clam
        self.layout.theme_use('clam')
        # button
        self.layout.layout('TButton', [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # radiobutton
        self.layout.layout('TRadiobutton', [('Radiobutton.padding', {'sticky': 'nswe', 'children': [('Radiobutton.label', {'sticky': 'nswe'})]})])
        # scrollbar
        self.layout.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])

    def init_ui(self) -> None:
        # variables
        self.theme: StringVar = StringVar(value='System')
        self.updates: BooleanVar = BooleanVar(value=True)
        # setup panels
        pages_panel: ttk.Frame  = ttk.Frame(self)
        pages_panel.pack(side='top', fill='both', expand=True)
        # progress
        self.progress_bar = ttk.Progressbar(self, maximum=self.pages * 100, value=0)
        self.progress_bar.pack(side='bottom', fill='x')
        # page 1
        welcome_panel: ttk.Frame  = ttk.Frame(pages_panel)
        welcome_content: ttk.Frame  = ttk.Frame(welcome_panel)
        ttk.Label(welcome_content, text='Welcome to Sounder5!', style='second.TLabel').pack(side='top', pady=10, anchor='center')
        ttk.Button(welcome_content, text='Start listening!', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(import_panel)).pack(side='top', pady=10, anchor='center')
        welcome_content.pack(anchor='center', padx=10, pady=10, expand=True)
        welcome_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 2
        import_panel: ttk.Frame  = ttk.Frame(pages_panel)
        ttk.Label(import_panel, text='Import settings!', style='second.TLabel').pack(side='top', anchor='center', pady=(10, 0))
        ttk.Label(import_panel, text='Import old settings or set up as new!', style='third.TLabel').pack(side='top', anchor='center')
        import_content: ttk.Frame = ttk.Frame(import_panel)
        ttk.Button(import_content, text='Set up as new', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(folder_panel)).pack(side='bottom', pady=10, anchor='center', fill='x')
        ttk.Button(import_content, text='Choose a settings file', image=self.icons['plus'], compound='right', style='second.TButton', command=self.import_settings).pack(side='bottom', pady=10, anchor='center', fill='x')
        import_content.pack(anchor='center', padx=10, pady=10, expand=True)
        import_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 3
        folder_panel: ttk.Frame  = ttk.Frame(pages_panel)
        folder_scrollbar: ttk.Scrollbar = ttk.Scrollbar(folder_panel)
        folder_scrollbar.pack(side='right', fill='y')
        ttk.Label(folder_panel, text='Let\'s start with music!', style='second.TLabel').pack(side='top', anchor='center', pady=(10, 0))
        ttk.Label(folder_panel, text='Show us where you store your music.', style='third.TLabel').pack(side='top', anchor='center')
        # player content
        folder_canvas: Canvas = Canvas(folder_panel, background=self['background'], bd=0, highlightthickness=0, yscrollcommand=folder_scrollbar.set, takefocus=False)
        # link scrollbar to canvas
        folder_scrollbar.configure(command=folder_canvas.yview)
        self.folder_panels: ttk.Frame  = ttk.Frame(folder_canvas)
        self.folder_panels.bind('<Configure>', lambda _: folder_canvas.configure(scrollregion=folder_canvas.bbox("all")))
        folder_window = folder_canvas.create_window((0, 0), window=self.folder_panels, anchor='nw')
        folder_canvas.bind('<Configure>', lambda _: folder_canvas.itemconfigure(folder_window, width=folder_canvas.winfo_width(), height=0))
        folder_canvas.pack(side='top', padx=10,  pady=10, anchor='center', fill='both')
        folder_buttons: ttk.Frame  = ttk.Frame(folder_panel)
        # add folder button
        ttk.Button(folder_buttons, text='Add folder', image=self.icons['plus'], compound='left', style='second.TButton', command=self.add_folder).pack(side='left', pady=5, padx=(10, 25))
        # skip / continue button
        self.folder_button = ttk.Button(folder_buttons, text='Skip', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(appearance_panel))
        self.folder_button.pack(side='right', pady=5, padx=(25, 10))
        folder_buttons.pack(side='bottom', pady=5)
        folder_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 4
        appearance_panel: ttk.Frame  = ttk.Frame(pages_panel)
        ttk.Label(appearance_panel, text='Theme!', style='second.TLabel').pack(side='top', anchor='center', pady=(10, 0))
        ttk.Label(appearance_panel, text='Shine bright like a star or be dark like a boss!', style='third.TLabel').pack(side='top', anchor='center')
        appearance_content: ttk.Frame  = ttk.Frame(appearance_panel)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='Light', compound='left', variable=self.theme, value='Light', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='Dark', compound='left', variable=self.theme, value='Dark', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='System', compound='left', variable=self.theme, value='System', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        appearance_content.pack(anchor='center', padx=10, pady=10, expand=True)
        ttk.Button(appearance_panel, text='Next', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(updates_panel)).pack(side='bottom', pady=10, anchor='center')
        appearance_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 5
        updates_panel: ttk.Frame  = ttk.Frame(pages_panel)
        ttk.Label(updates_panel, text='Updates!', style='second.TLabel').pack(side='top', anchor='center', pady=(10, 0))
        ttk.Label(updates_panel, text='That\'s right, everybody likes updates!', style='third.TLabel').pack(side='top', anchor='center')
        updates_content: ttk.Frame  = ttk.Frame(updates_panel)
        ttk.Radiobutton(updates_content, image=self.icons['checkmark'], text='Yes, check for updates!', compound='left', value=True, variable=self.updates, command=self.change_updates).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(updates_content, image=self.icons['delete'], text='No :(', compound='left', value=False, variable=self.updates, command=self.change_updates).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        updates_content.pack(anchor='center', padx=10, pady=10, expand=True)
        ttk.Button(updates_panel, text='Next', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(self.final_panel)).pack(side='bottom', pady=10, anchor='center')
        updates_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # final
        self.final_panel: ttk.Frame  = ttk.Frame(pages_panel)
        final_content: ttk.Frame  = ttk.Frame(self.final_panel)
        ttk.Label(final_content, text='That\'s all!', style='second.TLabel').pack(side='top', pady=10, anchor='center')
        ttk.Button(final_content, text='Finish', image=self.icons['checkmark'], compound='left', style='second.TButton', command=self.exit_app).pack(side='top', pady=10, anchor='center')
        final_content.pack(anchor='center', padx=10, pady=10, expand=True)
        self.final_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # show welcome panel 
        welcome_panel.lift()

    def load_icons(self) -> None:
        self.icons: dict = {
            'arrow': (PhotoImage(file=r'Resources\\Icons\\Configurator\\left.png'), PhotoImage(file=r'Resources\\Icons\\Configurator\\right.png')),
            'logo': PhotoImage(file=r'Resources\\Icons\\Configurator\\setup.png'),
            'plus': PhotoImage(file=r'Resources\\Icons\\Configurator\\plus.png'),
            'folder': PhotoImage(file=r'Resources\\Icons\\Configurator\\music_folder.png'),
            'delete': PhotoImage(file=r'Resources\\Icons\\Configurator\\delete.png'),
            'brush': PhotoImage(file=r'Resources\\Icons\\Configurator\\brush.png'),
            'checkmark': PhotoImage(file=r'Resources\\Icons\\Configurator\\checkmark.png')
        }
        self.iconphoto(False, self.icons['logo'])

    def apply_theme(self) -> None:
        # window 
        self.configure(background='#212121')
        # frame
        self.layout.configure('TFrame', background='#212121')
        self.layout.configure('second.TFrame', background='#111')
        # label
        self.layout.configure('TLabel', background='#111', relief='flat', font=('catamaran 13 bold'), foreground='#fff')
        self.layout.configure('second.TLabel', background='#212121', font=('catamaran 30 bold'), anchor='center')
        self.layout.configure('third.TLabel', background='#212121')
        # radiobutton
        self.layout.configure('TRadiobutton', background='#212121', relief='flat', font=('catamaran 13 bold'), foreground='#fff', anchor='w', padding=10, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', '#111'), ('active', '#111'), ('selected', '#111')])
        # button
        self.layout.configure('TButton', background='#111', relief='flat', font=('catamaran 13 bold'), foreground='#fff', anchor='w')
        self.layout.map('TButton', background=[('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])
        self.layout.configure('second.TButton', anchor='center')
        # scrollbar
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background='#212121', darkcolor='#212121', lightcolor='#212121', troughcolor='#212121', bordercolor='#212121')
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', '#111'), ('disabled', '#212121'), ('active', '#111'), ('!active', '#111')])   
        # scale
        self.layout.configure('Horizontal.TProgressbar', foreground='#111', background='#111', lightcolor='#111', darkcolor='#111', bordercolor='#212121', troughcolor='#212121')

    def add_folder(self) -> None:
        temp_dir: str = askdirectory()
        if temp_dir and not temp_dir in self.settings['folders']:
            temp_dir = abspath(temp_dir)
            # add folder to settings
            self.settings['folders'].append(temp_dir)
            # draw folder in app
            folder_panel: ttk.Frame  = ttk.Frame(self.folder_panels, style='second.TFrame')
            path_label = ttk.Label(folder_panel, image=self.icons['folder'], text=basename(temp_dir), compound='left')
            path_label.pack(side='left', anchor='center', fill='y', pady=10, padx=10)
            ttk.Button(folder_panel, image=self.icons['delete'], takefocus=False, command=lambda: self.remove_folder(folder_panel, temp_dir)).pack(side='right', padx=10, anchor='center')
            folder_panel.bind('<Leave>', lambda _:path_label.configure(text=basename(temp_dir)))
            folder_panel.bind('<Enter>', lambda _:path_label.configure(text=temp_dir))
            folder_panel.pack(side='top', fill='x', pady=5, padx=10)
            self.folder_button.configure(text='Continue')

    def remove_folder(self, panel, folder: str) -> None:
        if folder in self.settings['folders']:
            self.settings['folders'].remove(folder)
            panel.destroy()
            if len(self.settings['folders']) == 0:
                self.folder_button.configure(text='Skip')

    def change_theme(self) -> None:
        theme: str = self.theme.get()
        if theme != 'System':
            self.settings['use_system_theme'] = False
            self.settings['theme'] = theme

    def change_updates(self) -> None:
        self.settings['updates'] = self.updates.get()

    def next_page(self, page) -> None:
        Thread(target=self.update_progress, daemon=True).start()
        page.lift()

    def update_progress(self) -> None:
        for _ in range(10):
            self.progress_bar['value'] += 10
            sleep(0.01)
        if self.progress_bar['value'] == self.pages * 100:
            self.progress_bar['value'] = 0

    def animate_progress(self, value: int) -> None:
        for _ in range(int(value / 10)):
            self.progress_bar['value'] += 10
            sleep(0.001)
        if self.progress_bar['value'] == self.pages * 100:
            self.progress_bar['value'] = 0

    def import_settings(self) -> None:
        settings_file: str = askopenfilename(title='Open a settings file', initialdir='/', filetypes=(('Sounder settings files', '*.json'),))
        if settings_file:
            with open(settings_file, 'r') as data:
                try:
                    self.settings.update(load(data))
                    Thread(target=self.animate_progress, args=(400,), daemon=True).start()
                    self.final_panel.lift()
                except JSONDecodeError:
                    pass
