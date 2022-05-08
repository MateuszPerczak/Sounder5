from tkinter import Tk, ttk
from tkinter.filedialog import askdirectory
from os.path import basename, abspath, isfile, splitext, isdir, join
from os import listdir, remove
from hashlib import md5
from typing import Callable


class UpdateBuilder(Tk):
    def __init__(self: Tk) -> Tk:
        super().__init__()
        self.withdraw()
        self.title("Update Builder")
        self.geometry("400x200")
        self.resizable(False, False)
        self.iconbitmap('Resources\\Icons\\Light\\icon.ico')
        self.configure(background='#222')

        # variables
        self.new_update_path: str = ''
        self.old_update_path: str = ''

        # do stuff
        self.__init_layout__()
        self.__init_ui__()
        # show window
        self.deiconify()

    def __init_layout__(self: Tk) -> None:
        # layout
        self.layout: ttk.Style = ttk.Style()
        # set theme to clam
        self.layout.theme_use('clam')
        # button
        self.layout.layout('TButton', [('Button.padding', {
            'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        # theme
        self.configure(background='#212121')
        # panel
        self.layout.configure('TFrame', background='#212121')
        # button
        self.layout.configure('TButton', background='#111', relief='flat', font=(
            'catamaran 12 bold'), foreground='#fff')
        self.layout.map('TButton', background=[
                        ('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])

    def __init_ui__(self: Tk) -> None:
        # frame
        self.frame: ttk.Frame = ttk.Frame(self)
        self.new_update: ttk.Button = ttk.Button(
            self.frame, text='Select new update', command=lambda: self.select_directory('new'))
        self.new_update.pack(side='top', fill='x', padx=10, pady=(10, 0))

        self.old_update: ttk.Button = ttk.Button(
            self.frame, text='Select current update', command=lambda: self.select_directory('old'))
        self.old_update.pack(side='top', fill='x', padx=10, pady=(10, 0))

        ttk.Button(self.frame, text='Convert', command=self.__convert__).pack(
            side='top', fill='x', padx=10, pady=10)

        self.frame.place(relx=.5, rely=0.5, anchor='c', relwidth=.8)

    def select_directory(self: Tk, dir_type: str) -> None:
        directory: str = askdirectory(title='Select directory')
        if directory:
            if dir_type == 'new':
                self.new_update_path = directory
                self.new_update.configure(
                    text=f'Directory: {basename(directory)}')
            elif dir_type == 'old':
                self.old_update_path = directory
                self.old_update.configure(
                    text=f'Directory: {basename(directory)}')

    def get_md5(self: Tk, file: str) -> str:
        md5_obj: Callable = md5()
        with open(file, 'rb') as source:
            while True:
                data: bytes = source.read(65536)
                if not data:
                    break
                md5_obj.update(data)
        return md5_obj.hexdigest()

    def generate_hashes(self) -> None:
        self.hashes = {}
        for file in self.files:
            self.hashes[file] = self.get_md5(file)

    def get_tree(self: Tk, path: str) -> None:
        tree: list = [path, ]

        for folder in tree:
            for item in listdir(folder):
                if item in ('System Volume Information', '$RECYCLE.BIN'):
                    continue
                path = abspath(join(folder, item))
                if isdir(path) and not path in tree:
                    tree.append(path)
        return tree

    def get_files(self: Tk, folders: list) -> None:
        files: list = []
        path: str = ''
        for folder in folders:
            for item in listdir(folder):
                path = abspath(join(folder, item))
                if isfile(path) and not splitext(item)[1] in ('.ini'):
                    files.append(path)
        return files

    def __convert__(self: Tk) -> None:
        if self.new_update_path and self.old_update_path:
            new_tree = self.get_tree(self.new_update_path)
            old_tree = self.get_tree(self.old_update_path)

            new_files: list = self.get_files(new_tree)
            old_files: list = self.get_files(old_tree)

            new_hashes: dict = {}
            for file in new_files:
                new_hashes[file] = self.get_md5(file)

            old_hashes: list = []
            for file in old_files:
                old_hashes.append(self.get_md5(file))

            self.compare_files(new_hashes, old_hashes)

            # remove empty directoryies in new_tree
            for folder in listdir(self.new_update_path):
                if folder in ('System Volume Information', '$RECYCLE.BIN'):
                    continue
                print('-------------------------------')

                if isdir(folder):
                    print(folder, listdir(folder))
                    print('-------------------------------')
                    # if not :
                    #     remove(folder)
            print('done')

    def compare_files(self, new_hashes: dict, old_hashes: list) -> None:
        duplicates: list = []
        for file in new_hashes:
            if new_hashes[file] in old_hashes:
                duplicates.append(file)

        for file in duplicates:
            remove(file)


if __name__ == "__main__":
    UpdateBuilder().mainloop()
