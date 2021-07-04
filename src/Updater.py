try:
    from tkinter import Tk, ttk
    from time import sleep
    from sys import argv
    from os import remove, rename, startfile
    from os.path import basename, isfile
    from requests import get
    from zipfile import ZipFile
    from io import BytesIO
    from sys import exit
    from psutil import process_iter
    from threading import Thread
    # from Components.Debugger import Debugger
    from logging import basicConfig, error
    from PIL import Image, ImageSequence, ImageTk
    from time import sleep, strftime
    from traceback import format_exc
    from hashlib import sha256
    from json import dump, load
    from json.decoder import JSONDecodeError
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
        # self.bind('<F12>', lambda _: Debugger(self))
        self.init_logging()
        if self.self_update():
            self.exit_app()
        else:
            self.init_theme()
            self.load_icons()
            self.init_ui()
            Thread(target=self.animation, daemon=True).start()
            if self.get_version():
                if self.get_args():
                    if self.compare_version():
                        self.update_panel.lift()
                        Thread(target=self.update, daemon=True).start()
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
        ttk.Label(self.reinstall_panel, text='The latest version of Sounder is already installed.\nWould you like to reinstall it?').pack(side='top', pady=(10, 5), padx=5)
        reinstall_buttons: ttk.Frame = ttk.Frame(self.reinstall_panel)
        ttk.Button(reinstall_buttons, text='Reinstall', command=lambda: Thread(target=self.update, daemon=True).start()).pack(side='left', anchor='c', pady=(0, 5), padx=(10, 5))
        ttk.Button(reinstall_buttons, text='Exit', command=self.exit_app).pack(side='right', anchor='c', pady=(0, 5), padx=(5, 10))
        reinstall_buttons.pack(side='bottom', pady=(0, 10))
        self.reinstall_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # update panel
        self.update_panel: ttk.Frame = ttk.Frame(self)
        # update label
        self.progress_label: ttk.Label = ttk.Label(self.update_panel, text='Checking', image=self.icons['setup'], anchor='center', style='second.TLabel', compound='top')
        self.progress_label.pack(fil='both', side='top', expand=True)
        self.update_panel.place(x=0, y=0, relwidth=1, relheight=1)
        # finish panel
        self.finish_panel: ttk.Frame = ttk.Frame(self)
        ttk.Label(self.finish_panel, image=self.icons['checkmark'], text='All done!', compound='top').pack(side='top', pady=(10, 5), padx=5)
        finish_buttons: ttk.Frame = ttk.Frame(self.finish_panel)
        ttk.Button(finish_buttons, text='Exit', command=self.exit_app).pack(side='right', anchor='c', pady=(0, 5), padx=(5, 10))
        finish_buttons.pack(side='bottom', pady=(0, 10))
        self.finish_panel.place(x=0, y=0, relwidth=1, relheight=1)
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
        self.layout.configure('second.TLabel', font=('catamaran 16 bold'))
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
            'checkmark': ImageTk.PhotoImage(Image.open(r'Resources\\Icons\\Updater\\checkmark.png').resize((40, 40))),
            'loading': Image.open(r'Resources\\Icons\\Updater\\loading.gif')
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
            self.server_version: str = get('https://raw.githubusercontent.com/losek1/Sounder5/master/updates/version.txt').text.strip()
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

    def check_package(self) -> bool:
        self.update_package = get('https://raw.githubusercontent.com/losek1/Sounder5/master/updates/package.zip', stream=True)
        if self.update_package.status_code == 200:
            return True
        return False

    def get_package(self) -> bool:
        self.progress_label['text'] = 'Downloading 0%'
        bytes_downloaded: float = 0
        package_size: int = int(self.update_package.headers.get('Content-Length'))
        update_zip: bytes = b''
        for package in self.update_package.iter_content(chunk_size=8192):
            if package:
                update_zip += package
                bytes_downloaded += 8192
                self.progress_label['text'] = f'Downloading {int((bytes_downloaded * 100) / package_size)}%'
                sleep(0.001)
        self.progress_label['text'] = 'Verifying update'
        if self.verify_package(update_zip):
            del bytes_downloaded, package_size, self.update_package
            self.progress_label['text'] = 'Closing instances'
            self.kill_sounder()
            self.progress_label['text'] = 'Applying update 0%'
            with ZipFile(BytesIO(update_zip)) as zip_file:
                update_files = zip_file.namelist()
                files_to_update: int = len(update_files)
                for file in update_files:
                    self.progress_label['text'] = f'Applying update {int((update_files.index(file) * 100) / files_to_update)}%'
                    if file.find('Resources/Settings/') or file == 'Updater.exe':
                        continue
                    try:
                        zip_file.extract(file, r'./')
                    except Exception as err_obj:
                        self.log(err_obj, 'Unabe to apply update!')
            self.progress_label['text'] = 'Registering update 0%'
            self.update_history()
            self.progress_label['text'] = 'Registering update 100%'
            sleep(0.5)
            self.progress_label['text'] = 'Applying update 100%'
            self.finish_panel.lift()
            sleep(2)
            self.progress_label['text'] = 'Launching Sounder'
            sleep(0.5)
            self.after_update()
        else:
            self.err_label['text'] = 'Unable to verify update!'
            self.err_panel.lift()

    def verify_package(self, package_bytes: bytes) -> bool:
        try:
            self.server_hash: str = get('https://raw.githubusercontent.com/losek1/Sounder5/master/updates/hash.txt').text.strip()
        except Exception as err_obj:
            self.log(err_obj, 'Unable to connect to server!')
            return False
        package_hash: str = sha256(package_bytes).hexdigest()
        if package_hash == self.server_hash:
            return True
        return False

    def update(self) -> None:
        try:
            self.update_panel.lift()
            if self.check_package():
                self.get_package()
            else:
                self.progress_label['text'] = ''
                self.err_label['text'] = 'Unable to download update'
                self.err_panel.lift()
        except Exception as err_obj:
            self.log(err_obj, 'Something went wrong!')

    def animation(self) -> None:
        image_frames: list = []
        for frame in ImageSequence.Iterator(self.icons['loading']):
            image_frames.append(ImageTk.PhotoImage(frame.copy().convert('RGBA').resize((48, 48))))
        if len(image_frames) > 1:
            while True:
                for frame in image_frames:
                    self.progress_label.configure(image=frame)
                    sleep(0.025)
        else:
            self.progress_label.configure(image=image_frames)  

    def update_history(self) -> None:
        updates_history: dict = {'Updates': []}
        # read history
        if isfile(r'Resources\\Settings\\Updates.json'):
            with open(r'Resources\\Settings\\Updates.json', 'r') as data:
                try:
                    updates_history = load(data)
                except JSONDecodeError as _:
                    updates_history = {'Updates': [{'Version': self.server_version, 'Date': strftime('%d-%m-%Y'), 'Hash': self.server_hash}]}
        else:
            updates_history['Updates'].append({'Version': self.server_version, 'Date': strftime('%d-%m-%Y'), 'Hash': self.server_hash})
        # update history
        with open(r'Resources\\Settings\\Updates.json', 'w') as data:
            try:
                dump(updates_history, data)
            except Exception as _:
                pass

    def after_update(self) -> None:
        if isfile('Sounder5.exe'):
            startfile('Sounder5.exe')

if __name__ == '__main__':
    Updater().mainloop()