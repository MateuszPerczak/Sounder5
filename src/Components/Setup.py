try:
    from tkinter import Toplevel, ttk, Canvas, StringVar, BooleanVar
    from tkinter.filedialog import askdirectory
    from typing import ClassVar
    from Components.Debugger import Debugger
    from os.path import isfile, join, isdir, basename, abspath, join
    from time import sleep
    from PIL import Image, ImageTk
    from threading import Thread
except ImportError as err:
    exit(err)


class SSetup(Toplevel):
    def __init__(self: ClassVar, parent: ClassVar, settings: dict) -> None:
        super().__init__(parent)
        # variables
        self.settings = settings
        self.parent = parent
        # hide window
        self.withdraw()
        # configure window
        self.minsize(500, 620)
        self.resizable(False, False)
        self.title('Sounder configurator')
        self.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.bind('<F12>', lambda _: Debugger(self))
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

    def exit_app(self: ClassVar) -> None:
        self.quit()
        self.destroy()
        
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

    def init_ui(self: ClassVar) -> None:
        # variables
        self.theme: StringVar = StringVar(value='System')
        self.updates: BooleanVar = BooleanVar(value=True)
        # setup panels
        pages_panel: ClassVar = ttk.Frame(self)
        pages_panel.pack(side='top', fill='both', expand=True)
        # progress
        self.progress_bar: ClassVar = ttk.Progressbar(self, maximum=400, value=0)
        self.progress_bar.pack(side='bottom', fill='x')
        # page 1
        welcome_panel: ClassVar = ttk.Frame(pages_panel)
        welcome_content: ClassVar = ttk.Frame(welcome_panel)
        ttk.Label(welcome_content, text='Welcome to Sounder5!', style='second.TLabel').pack(side='top', pady=10, anchor='c')
        ttk.Button(welcome_content, text='Start listening!', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(folder_panel)).pack(side='top', pady=10, anchor='c')
        welcome_content.pack(anchor='c', padx=10, pady=10, expand=True)
        welcome_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 2
        folder_panel: ClassVar = ttk.Frame(pages_panel)
        folder_scrollbar: ClassVar = ttk.Scrollbar(folder_panel)
        folder_scrollbar.pack(side='right', fill='y')
        ttk.Label(folder_panel, text='Let\'s start with music!', style='second.TLabel').pack(side='top', anchor='c', pady=(10, 0))
        ttk.Label(folder_panel, text='Show us where you store your music.', style='third.TLabel').pack(side='top', anchor='c')
        # player content
        folder_canvas: ClassVar = Canvas(folder_panel, background=self['background'], bd=0, highlightthickness=0, yscrollcommand=folder_scrollbar.set, takefocus=False)
        # link scrollbar to canvas
        folder_scrollbar.configure(command=folder_canvas.yview)
        self.folder_panels: ClassVar = ttk.Frame(folder_canvas)
        self.folder_panels.bind('<Configure>', lambda _: folder_canvas.configure(scrollregion=folder_canvas.bbox("all")))
        folder_window: ClassVar = folder_canvas.create_window((0, 0), window=self.folder_panels, anchor='nw')
        folder_canvas.bind('<Configure>', lambda _: folder_canvas.itemconfigure(folder_window, width=folder_canvas.winfo_width(), height=0))
        folder_canvas.pack(side='top', padx=10,  pady=10, anchor='c', expand=True, fill='both')
        folder_buttons: ClassVar = ttk.Frame(folder_panel)
        # add folder button
        ttk.Button(folder_buttons, text='Add folder', image=self.icons['plus'], compound='left', style='second.TButton', command=self.add_folder).pack(side='left', pady=5, padx=(10, 25))
        # skip / continue button
        self.folder_button: ClassVar = ttk.Button(folder_buttons, text='Skip', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(appearance_panel))
        self.folder_button.pack(side='right', pady=5, padx=(25, 10))
        folder_buttons.pack(side='bottom', pady=5)
        folder_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 3
        appearance_panel: ClassVar = ttk.Frame(pages_panel)
        ttk.Label(appearance_panel, text='Theme!', style='second.TLabel').pack(side='top', anchor='c', pady=(10, 0))
        ttk.Label(appearance_panel, text='Shine bright like a star or be dark like a boss!', style='third.TLabel').pack(side='top', anchor='c')
        appearance_content: ClassVar = ttk.Frame(appearance_panel)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='Light', compound='left', variable=self.theme, value='Light', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='Dark', compound='left', variable=self.theme, value='Dark', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(appearance_content, image=self.icons['brush'], text='System', compound='left', variable=self.theme, value='System', command=self.change_theme).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        appearance_content.pack(anchor='c', padx=10, pady=10, expand=True)
        ttk.Button(appearance_panel, text='Next', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(updates_panel)).pack(side='bottom', pady=10, anchor='c')
        appearance_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # page 4
        updates_panel: ClassVar = ttk.Frame(pages_panel)
        ttk.Label(updates_panel, text='Updates!', style='second.TLabel').pack(side='top', anchor='c', pady=(10, 0))
        ttk.Label(updates_panel, text='That\'s right, everybody likes updates!', style='third.TLabel').pack(side='top', anchor='c')
        updates_content: ClassVar = ttk.Frame(updates_panel)
        ttk.Radiobutton(updates_content, image=self.icons['checkmark'], text='Yes, check for updates!', compound='left', value=True, variable=self.updates, command=self.change_updates).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        ttk.Radiobutton(updates_content, image=self.icons['delete'], text='No :(', compound='left', value=False, variable=self.updates, command=self.change_updates).pack(side='top', fill='x', padx=10, pady=5, ipadx=45)
        updates_content.pack(anchor='c', padx=10, pady=10, expand=True)
        ttk.Button(updates_panel, text='Next', image=self.icons['arrow'][1], compound='right', style='second.TButton', command=lambda: self.next_page(final_panel)).pack(side='bottom', pady=10, anchor='c')
        updates_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # final 
        final_panel: ClassVar = ttk.Frame(pages_panel)
        final_content: ClassVar = ttk.Frame(final_panel)
        ttk.Label(final_content, text='That\'s all!', style='second.TLabel').pack(side='top', pady=10, anchor='c')
        ttk.Button(final_content, text='Finish', image=self.icons['checkmark'], compound='right', style='second.TButton', command=self.exit_app).pack(side='top', pady=10, anchor='c')
        final_content.pack(anchor='c', padx=10, pady=10, expand=True)
        final_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # show welcome panel 
        welcome_panel.lift()

    def load_icons(self: ClassVar) -> None:
        self.icons: dict = {
            'arrow': (ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\left.png').resize((25, 25))), ImageTk.PhotoImage(Image.open('Resources\\Icons\\Dark\\right.png').resize((25, 25)))),
            'logo': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\setup.png')),
            'plus': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\plus.png').resize((25, 25))),
            'folder': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\music_folder.png').resize((25, 25))),
            'delete': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\delete.png').resize((25, 25))),
            'brush': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\brush.png').resize((25, 25))),
            'checkmark': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Configurator\\checkmark.png').resize((25, 25))),
        }
        self.iconphoto(False, self.icons['logo'])

    def apply_theme(self: ClassVar) -> None:
        # window 
        self.configure(background='#212121')
        # frame
        self.layout.configure('TFrame', background='#212121')
        self.layout.configure('second.TFrame', background='#111')
        # label
        self.layout.configure('TLabel', background='#111', relief='flat', font=('catamaran 13 bold'), foreground='#fff')
        self.layout.configure('second.TLabel', background='#212121', font=('catamaran 30 bold'), anchor='c')
        self.layout.configure('third.TLabel', background='#212121')
        # radiobutton
        self.layout.configure('TRadiobutton', background='#212121', relief='flat', font=('catamaran 13 bold'), foreground='#fff', anchor='w', padding=10, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', '#111'), ('active', '#111'), ('selected', '#111')])
        # button
        self.layout.configure('TButton', background='#111', relief='flat', font=('catamaran 13 bold'), foreground='#fff', anchor='w')
        self.layout.map('TButton', background=[('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])
        self.layout.configure('second.TButton', anchor='c')
        self.layout.configure('third.TButton', anchor='c', background='#fff', foreground='#000')
        self.layout.map('third.TButton', background=[('pressed', '!disabled', '#eee'), ('active', '#eee'), ('selected', '#eee')])
        # scrollbar
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background='#212121', darkcolor='#212121', lightcolor='#212121', troughcolor='#212121', bordercolor='#212121')
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', '#111'), ('disabled', '#212121'), ('active', '#111'), ('!active', '#111')])   
        # scale
        self.layout.configure('Horizontal.TProgressbar', foreground='#111', background='#111', lightcolor='#111', darkcolor='#111', bordercolor='#212121', troughcolor='#212121')

    def add_folder(self: ClassVar) -> None:
        temp_dir: str = askdirectory()
        if temp_dir and not temp_dir in self.settings['folders']:
            # add folder to settings
            self.settings['folders'].append(temp_dir)
            # draw folder in app
            folder_panel: ClassVar = ttk.Frame(self.folder_panels, style='second.TFrame')
            path_label: ClassVar = ttk.Label(folder_panel, image=self.icons['folder'], text=basename(temp_dir), compound='left')
            path_label.pack(side='left', anchor='c', fill='y', pady=10, padx=10)
            ttk.Button(folder_panel, image=self.icons['delete'], takefocus=False, command=lambda: self.remove_folder(folder_panel, temp_dir)).pack(side='right', padx=10, anchor='c')
            folder_panel.bind('<Leave>', lambda _:path_label.configure(text=basename(temp_dir)))
            folder_panel.bind('<Enter>', lambda _:path_label.configure(text=temp_dir))
            folder_panel.pack(side='top', fill='x', pady=5, padx=10)
            self.folder_button.configure(text='Continue')

    def remove_folder(self: ClassVar, panel: ClassVar, folder: str) -> None:
        if folder in self.settings['folders']:
            self.settings['folders'].remove(folder)
            panel.destroy()
            if len(self.settings['folders']) == 0:
                self.folder_button.configure(text='Skip')

    def change_theme(self: ClassVar) -> None:
        theme: str = self.theme.get()
        if theme != 'System':
            self.settings['use_system_theme'] = False
            self.settings['theme'] = theme
        del theme

    def change_updates(self: ClassVar) -> None:
        self.settings['updates'] = self.updates.get()

    def next_page(self: ClassVar, page: ClassVar) -> None:
        Thread(target=self.animate_progress, args=(100, ), daemon=True).start()
        page.lift()

    def animate_progress(self: ClassVar, value: int) -> None:
        for _ in range(int((value + 4) / 8)):
            self.progress_bar['value'] += 8
            sleep(0.0001)
        if self.progress_bar['value'] > 400:
            self.progress_bar['value'] = 0

