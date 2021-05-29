try:
    from typing import ClassVar
    from tkinter import Tk, ttk
    from time import sleep
    from sys import argv
    from os import remove, rename, startfile
    from os.path import basename, isfile
    from requests import get
    from sys import exit
    from psutil import process_iter
    from threading import Thread
    from Components.Debugger import Debugger
    from logging import basicConfig, error, getLevelName, getLogger, shutdown
    from PIL import Image, ImageSequence, ImageTk
    from time import sleep
    from traceback import format_exc
except ImportError as err:
    exit(err)


class Updater(Tk):
    def __init__(self) -> None:
        super().__init__()
        # hide window
        self.withdraw()
        # configure window
        self.geometry(f'400x150+{int((self.winfo_screenwidth() / 2) - 200)}+{int((self.winfo_screenheight() / 2) - 75)}')
        self.title('Sounder updater')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.bind('<F12>', lambda _: Debugger(self))
        self.init_logging()
        if self.self_update():
            self.exit_app()
        else:
            self.init_theme()
            self.load_icons()
            self.init_ui()
            Thread(target=self.animation, daemon=True).start()
            if self.get_args():
                if self.get_version():
                    if self.compare_version():
                        self.update_panel.lift()
                        self.update(False)
                    else:
                        self.reinstall_panel.lift()
            else:
                self.reinstall_panel.lift()

    def exit_app(self) -> None:
        self.destroy()
        self.quit()

    def init_logging(self) -> None:
        # logging error messages
        basicConfig(filename=f'Resources\\Dumps\\dump.txt', level=40)

    def log(self, err_obj, err_text: str) -> None:
        # DING!!!!!!
        self.bell()
        self.err_label['text'] = err_text if err_text else format_exc().split("\n")[-2]
        self.err_panel.lift()
        error(err_obj, exc_info=True)

    def self_update(self) -> bool:
        # check instance name
        if basename(argv[0]) == 'New-Updater.exe':
            if isfile('Updater.exe'): remove('Updater.exe')
            rename(argv[0], 'Updater.exe')
        elif isfile('New-Updater.exe'):
            startfile('New-Updater.exe')
            return True
        return False

    def init_ui(self) -> None:
        # variables
        # error panel
        self.err_panel: ttk.Frame = ttk.Frame(self)
        self.err_label: ttk.Label = ttk.Label(self.err_panel, image=self.icons['error'], text='Unable to display the error message!', compound='top')
        self.err_label.pack(side='top', anchor='c', pady=(10, 5))
        ttk.Button(self.err_panel, text='Exit', command=self.exit_app).pack(side='bottom', anchor='c', pady=(0, 10))
        self.err_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # init panel
        init_panel: ttk.Frame = ttk.Frame(self)
        ttk.Label(init_panel, text='Checking ...').pack(side='top', anchor='c', expand=True, pady=(10, 5))
        init_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # reinstall panel
        self.reinstall_panel: ttk.Frame = ttk.Frame(self)
        ttk.Label(self.reinstall_panel, text='The latest version of Sounder is already installed.\nWould you like to reinstall it?').pack(side='top', pady=(10, 5))
        reinstall_buttons: ttk.Frame = ttk.Frame(self.reinstall_panel)
        ttk.Button(reinstall_buttons, text='Reinstall', command=lambda: self.update(True)).pack(side='left', anchor='c', pady=(0, 5), padx=(10, 5))
        ttk.Button(reinstall_buttons, text='Exit', command=self.exit_app).pack(side='right', anchor='c', pady=(0, 5), padx=(5, 10))
        reinstall_buttons.pack(side='bottom', pady=(0, 10))
        self.reinstall_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # update panel
        self.update_panel: ttk.Frame = ttk.Frame(self)

        # update label
        self.progress_label: ttk.Label = ttk.Label(self.update_panel, text='Updating 0%', image=self.icons['setup'], anchor='center', style='second.TLabel', compound='top')

        # progress bar
        self.progress: ttk.Progressbar = ttk.Progressbar(self.update_panel, mode='indeterminate')
        # self.progress.start(8)
        self.progress.pack(fill='x', side='bottom')
        self.progress_label.pack(fil='both', side='top', expand=True)
        self.update_panel.place(x=0, y=0, relwidth=1, relheight=1)

        # show init window
        init_panel.lift()

        # show window
        self.deiconify()


    def init_theme(self) -> None:
        # layout
        self.layout: ttk.Style = ttk.Style()
        # set theme to clam
        self.layout.theme_use('clam')
        # button
        self.layout.layout('TButton', [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # theme
        self.configure(background='#212121')
        # label
        self.layout.configure('TLabel', background='#212121', font=('catamaran 13 bold'), foreground='#fff', anchor='c')
        self.layout.configure('second.TLabel', font=('catamaran 20 bold'))
        # panel
        self.layout.configure('TFrame', background='#212121')
        # button
        self.layout.configure('TButton', background='#111', relief='flat', font=('catamaran 12 bold'), foreground='#fff')
        self.layout.map('TButton', background=[('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])
        # progressbar
        self.layout.configure('Horizontal.TProgressbar', foreground='#111', background='#111', lightcolor='#111', darkcolor='#111', bordercolor='#212121', troughcolor='#212121')

    def load_icons(self) -> None:
        self.icons: dict = {
            'setup': ImageTk.PhotoImage(Image.open(r'Resources\\Icons\\Updater\\setup.png').resize((75, 75))),
            'error': ImageTk.PhotoImage(Image.open(r'Resources\\Icons\\Updater\\error.png').resize((50, 50))),
            'cat': Image.open(r'Resources\\Icons\\Updater\\cat.gif')
        }
        self.iconphoto(False, self.icons['setup'])

    def get_args(self) -> bool:
        self.version: str = '0.0.0'
        if len(argv) == 2:
            self.version = argv[1]
            return True
        return False

    def get_version(self) -> bool:
        try:
            # self.server_version: str = get('https://raw.githubusercontent.com/losek1/Sounder5/master/updates/version.txt').text
            self.server_version: str = '3.1.0'
            return True
        except Exception as err_obj:
            self.log(err_obj, 'Unable to connect to server!')
            return False

    def compare_version(self) -> bool:
        try:
            return self.server_version != self.version and int(self.server_version.replace('.', '')) > int(self.version.replace('.', ''))
        except Exception as err_obj:
            self.log(err_obj, 'Unabe to convert server version!')
            return False

    def kill_sounder(self) -> None:
        for process in process_iter():
            if process.name() == "Sounder5.exe":
                process.kill()

    def update(self, ignore_version: bool = False) -> None:
        self.update_panel.lift()
        self.kill_sounder()



        print('update', ignore_version)

    def animation(self) -> None:
        image_frames: list = []
        for frame in ImageSequence.Iterator(self.icons['cat']):
            image_frames.append(ImageTk.PhotoImage(frame.copy().convert('RGBA').resize((48, 48))))
        if len(image_frames) > 1:
            while True:
                for frame in image_frames:
                    self.progress_label.configure(image=frame)
                    sleep(0.02)
        else:
            self.progress_label.configure(image=image_frames)  

# class Updater:
#     def __init__(self) -> None:
#         # check if newer updater is available
#         if not self.self_update():
#             self.init_logging()
#             self.init_ui()
#             if self.get_args():
#                 if self.get_version():
#                     if self.compare_version():
#                         self.kill_sounder()
#                         while not self.gui.window.winfo_ismapped(): 
#                             sleep(1)
#                         self.gui.update_panel.lift()
#                         if self.prepare_update():
#                             self.update()
#                     else:
#                         print('UP TO DATE')
#                 else:
#                     print('ERROR')
                
#             else:
#                 print('MODIFY MODE')


#     def log(self, err_obj, err_text: str = '') -> None:
#         # DING!!!!!!
#         self.gui.window.bell()
#         if err_text:
#             self.gui.err_label['text'] = err_text
#         else:
#             self.gui.err_label['text'] = format_exc().split("\n")[-2]
#         self.gui.error_panel.lift()
#         # log error to file
#         error(err_obj, exc_info=True)


#     def kill_sounder(self) -> None:
#         for process in process_iter():
#             if process.name() == "Sounder5.exe":
#                 process.kill()
    

#     def update(self) -> None:
#         try:
#             chunk_size: int = 4096
#             bytes_downloaded: float = 0
#             server_zip = get(f'https://github.com/losek1/Sounder3/releases/download/v{self.server_version}/package.zip', stream=True)
#             if server_zip.status_code == 200:
#                 for chunk in server_zip.iter_content(chunk_size=chunk_size):
#                     if chunk:
#                         bytes_downloaded += chunk_size
#                         print(bytes_downloaded)
                    
#             else:
#                 raise Exception('Unable to connect to server!')
#         except Exception as err_obj:
#             self.log(err_obj)


# class Updater_Gui(Thread):
#     def __init__(self) -> None:
#         Thread.__init__(self)
#         self.start()

#     def load_icons(self) -> None:
#         self.icons: dict = {
#             'logo': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Dark\\logo.png').resize((25, 25))),
#             'checkmark': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Dark\\checkmark.png').resize((25, 25))),
#             'delete': ImageTk.PhotoImage(Image.open('Resources\\Icons\\Dark\\delete.png').resize((25, 25))),
#         }
#         self.window.iconphoto(False, self.icons['logo'])

#     def exit_app(self) -> None:
#         self.window.quit()

#     def on_exit(self, func) -> None:
#         self.window.protocol('WM_DELETE_WINDOW', func)

#     def run(self) -> None:
#         self.window = Tk()
#         # hide window
#         self.window.withdraw()
#         # configure window
#         self.window.geometry(f'400x150+{int((self.window.winfo_screenwidth() / 2) - 200)}+{int((self.window.winfo_screenheight() / 2) - 150)}')
#         self.window.resizable(False, False)
#         self.window.title('Sounder updater')
#         self.window.protocol('WM_DELETE_WINDOW', self.exit_app)
#         self.window.bind('<F12>', lambda _: Debugger(self.window))
#         # load icons
#         self.load_icons()
#         # panels
#         # error panel
#         self.error_panel = ttk.Frame(self.window, style='second.TFrame')
#         self.err_label = ttk.Label(self.error_panel, text='We are unable to display the error message!', wraplength=380)
#         self.err_label.pack(side='top', fill='x', expand=True, padx=10, pady=(10, 0), anchor='c')
#         ttk.Button(self.error_panel, text='Exit', command=self.exit_app).pack(side='bottom', pady=(0, 10), anchor='c')
#         self.error_panel.place(x=0, y=0, relwidth=1, relheight=1)
#         # init panel
#         init_panel = ttk.Frame(self.window, style='second.TFrame')
#         ttk.Label(init_panel, image=self.icons['logo'], text='Sounder updater', compound='left').pack(side='top', fill='x', expand=True, padx=10, anchor='c')
#         init_panel.place(x=0, y=0, relwidth=1, relheight=1)
#         # update panel
#         self.update_panel = ttk.Frame(self.window, style='second.TFrame')




#         self.update_panel.place(x=0, y=0, relwidth=1, relheight=1)


#         # show window
#         init_panel.lift()
#         self.window.deiconify()
#         self.window.mainloop()


if __name__ == '__main__':
    Updater().mainloop()