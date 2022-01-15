try:
    from python_minifier import minify
    from os import mkdir, getcwd, remove, chdir
    from os.path import exists, join, abspath, expanduser
    from shutil import copytree, rmtree, move
    from json import dump
    from tkinter import Tk, ttk, Text
    from sys import platform, winver
    from time import sleep, perf_counter
    from threading import Thread
    from subprocess import Popen, PIPE, STDOUT, CalledProcessError
except ImportError as err_obj:
    exit(err_obj)

# current_dir = getcwd()

# # prepare files to minify

# files_to_minify: tuple = ('Sounder5.py', 'Updater.py', 'Components\\Setup.py', 'Components\\SongMenu.py', 'Components\\SystemTheme.py', 'Components\\DirWatcher.py', 'Components\\FontManager.py')

# # prepare folder for minified files
# if not exists('build'):
#     mkdir('build')
#     mkdir('build\\Components')
#     copytree('Resources', 'build\\Resources')
#     remove('build\\Resources\\Settings\\Settings.json')
#     with open('build\\Resources\\Settings\\Updates.json', 'w') as data:
#         dump({"Updates": []}, data)


# # minify all
# for file in files_to_minify:
#     minified_content: str = ''
#     with open(file, 'r') as data:
#         minified_content = minify(data.read()) # , rename_globals=True, rename_locals=True, hoist_literals=True
#     if minified_content:
#         with open(f'build\\{file}', 'w') as data:
#             data.write(minified_content)


class Builder(Tk):
    def __init__(self: object) -> None:
        super().__init__()
        # basic init of app
        self.title('Sounder5 Builder')
        self.iconbitmap('Resources\\Icons\\Light\\icon.ico')
        self.geometry('900x500')
        self.configure(background='#222')

        self.__init_layout__()
        self.__init_ui__()
        self.__say_hi__()

        '''
        SETUP
        '''
        # set follow
        self.follow: bool = True
        # get current_dir
        self.cwd = getcwd()

        self.user_desktop: str = join(expanduser("~"), "Desktop")
        # file to minify
        self.files_to_minify: tuple = ('Sounder5.py', 'Updater.py', 'Components\\Setup.py', 'Components\\ComboBox.py',
                                       'Components\\SongMenu.py', 'Components\\SystemTheme.py', 'Components\\DirWatcher.py', 'Components\\FontManager.py')
        # updater setup
        self.build_updater: list = ['pyinstaller', '-w', '--onefile', '--uac-admin',
                                    '-i', abspath('Resources\\Icons\\Updater\\setup.ico'), 'Updater.py']
        # sounder setup
        self.build_sounder: list = [
            'pyinstaller', '-w', '-i', abspath('Resources\\Icons\\Light\\icon.ico'), 'Sounder5.py']

    def __init_layout__(self: object) -> None:
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
        # scrollbar
        self.layout.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [
                           ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background='#212121',
                              darkcolor='#212121', lightcolor='#212121', troughcolor='#212121', bordercolor='#212121')
        self.layout.map('Vertical.TScrollbar', background=[
                        ('pressed', '!disabled', '#111'), ('disabled', '#212121'), ('active', '#111'), ('!active', '#111')])

    def __init_ui__(self: object) -> None:
        # init UI
        main_frame: ttk.Frame = ttk.Frame(self)
        # place scrollbar
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side='right', fill='y')
        # consolde frame
        left_frame: ttk.Frame = ttk.Frame(main_frame)
        # init console
        self.console: Text = Text(left_frame, state='disabled', background='#212121', foreground='#fff', selectbackground="#ecf0f1",
                                  selectforeground="#212121", bd=0, cursor="arrow", takefocus=0, font=('Catamaran bold', 10), yscrollcommand=scrollbar.set)
        # configure tags
        self.console.tag_config(
            'err', background='#212121', foreground='#c0392b')
        self.console.tag_config(
            'info', background='#212121', foreground='#ecf0f1')
        self.console.tag_config(
            'warning', background='#212121', foreground='#f1c40f')
        self.console.tag_config(
            'embeded', background='#212121', foreground='#2980b9')
        self.console.tag_config(
            'success', background='#212121', foreground='#27ae60')
        # attach scrollbar to console
        scrollbar.configure(command=self.console.yview)
        self.console.pack(side='left', fill='both',
                          expand=True, padx=10, pady=10)
        left_frame.pack(side='left', fill='both', expand=True)
        main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # build button
        buttons_frame: ttk.Frame = ttk.Frame(self)
        self.build_button: ttk.Button = ttk.Button(
            buttons_frame, text='Build', takefocus=False, command=self.build)
        self.build_button.pack(side='left', padx=5)
        ttk.Button(buttons_frame, text='Follow output', takefocus=False,
                   command=self.change_follow).pack(side='left', padx=5)
        buttons_frame.place(relx=0.95, rely=0.95, anchor='se')

    def change_follow(self: object) -> None:
        self.follow = not self.follow
        self.__push_msg_(
            f'Follow console output: {"Enabled" if self.follow else "Disabled"}', type='warning')

    def __say_hi__(self: object) -> None:
        self.console.configure(state='normal')
        self.console.insert('end', 'Sounder build tool v1.0.0\n')
        self.console.insert('end', f'Python {winver} {platform}\n')
        self.console.configure(state='disabled')

    def __push_msg_(self: object, message: str, type: str = 'info') -> None:
        self.console.configure(state='normal')
        self.console.insert('end', f'{message.strip()} \n', type)
        self.console.configure(state='disabled')
        if self.follow:
            self.console.see('end')
        if type == 'err':
            self.build_button.state(['!disabled'])

    def build(self: object) -> None:
        self.console.configure(state='normal')
        self.console.insert('end', 'Building Sounder5 ...\n')
        self.console.configure(state='disabled')
        self.build_button.state(['disabled'])
        Thread(target=self.build_process, daemon=True).start()

    def build_process(self: object) -> None:
        start = perf_counter()
        # make nesesery folders
        self.__push_msg_('Preparing folders ...')
        if exists('Build'):
            self.__push_msg_('Removed old build folder!', type='warning')
            rmtree('Build')
            sleep(2)
        self.__push_msg_('Preparing build folder ...')
        if not self.__make_folders():
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None

        self.__push_msg_('Minifying files ...')
        if not self.__minify_files(self.files_to_minify):
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_('Preparing console', type='warning')
        self.__push_msg_('Compiling Updater ...')
        # compile updater
        chdir(join(self.cwd, 'Build'))
        self.__push_msg_('Switching directory to Build')
        self.__push_msg_(
            f'Using shell commands {self.build_updater}', type='warning')
        if not self.__console_output(self.build_updater):
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_('Updater compiled!', type='success')
        self.__push_msg_('Preparing folders ...')
        self.__push_msg_('Switching directory to Desktop')
        chdir(self.user_desktop)
        if exists('Sounder files'):
            self.__push_msg_('Removed old build folder!', type='warning')
            rmtree('Sounder files')
            sleep(2)
        self.__push_msg_('Creating new build folder!', type='warning')
        mkdir('Sounder files')
        sleep(1)
        if not self.__copy_updater():
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_('Switching directory to Build')
        chdir(join(self.cwd, 'Build'))
        if exists('dist'):
            self.__push_msg_('Removing dist folder')
            rmtree('dist')
            sleep(2)
        if exists('build'):
            self.__push_msg_('Removing build folder')
            rmtree('build')
            sleep(2)
        self.__push_msg_('Preparing console', type='warning')
        self.__push_msg_(
            f'Using shell commands {self.build_sounder}', type='warning')
        self.__push_msg_('Compiling Sounder ...')
        if not self.__console_output(self.build_sounder):
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_('Sounder compiled!', type='success')
        self.__push_msg_('Switching directory to Desktop')
        chdir(self.user_desktop)
        if not self.__copy_sounder():
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_('Copying folders ...')
        if not self.__copy_folders():
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        self.__push_msg_(
            'Succesfouly copied: Resourcess, Components', type='success')
        self.__push_msg_('Switching directory to Sounder')
        chdir(self.cwd)
        self.__push_msg_('Cleaning up ...')
        if not self.__clean_up():
            self.__push_msg_('Stopping due to encounter error', type='err')
            return None
        end = perf_counter()
        self.__push_msg_(
            f'Task completed successfully in {end - start:0.4f} seconds', type='success')
        self.build_button.state(['!disabled'])

    '''
    Below build stuff
    '''

    def __make_folders(self: object) -> bool:
        try:
            mkdir('Build')
            mkdir('Build\\Components')
            copytree('Resources', 'Build\\Resources')
            remove('Build\\Resources\\Settings\\Settings.json')
            with open('Build\\Resources\\Settings\\Updates.json', 'w') as data:
                dump(
                    {"Updates": [{"Version": "0.8.1", "Date": "11-12-2021", "Hash": "Local"}]}, data)
            return True
        except Exception as err_obj:
            self.__push_msg_(f'Error: {err_obj}', type='err')
            return False

    def __minify_files(self: object, files_to_minify: str) -> bool:
        for file in files_to_minify:
            try:
                with open(file, 'r') as data:
                    # , rename_globals=True, rename_locals=True, hoist_literals=True
                    minified_content = minify(data.read())
                if minified_content:
                    with open(f'build\\{file}', 'w') as data:
                        data.write(minified_content)
                    self.__push_msg_(f'Minified {file}')
            except Exception as err_obj:
                self.__push_msg_(f'Error: {err_obj}', type='err')
                return False
        return True

    def __console_output(self: object, command: str) -> bool:
        try:
            shell: Popen = Popen(command, stdout=PIPE, stderr=STDOUT)
            # capture output
            for line in iter(shell.stdout.readline, b''):
                self.__push_msg_(line.decode('utf-8'), type='embeded')
            # wait for shell to finish
            shell.wait()
            return True
        except CalledProcessError as err_obj:
            self.__push_msg_(f'Error: {err_obj.output}', type='err')
            return False

    def __copy_updater(self: object) -> bool:
        try:
            if exists('Sounder files'):
                move(join(self.cwd, 'Build', 'dist', 'Updater.exe'),
                     join(self.user_desktop, 'Sounder files'))
                return True
            return False
        except Exception as err_obj:
            self.__push_msg_(f'Error: {err_obj}', type='err')
            return False

    def __copy_sounder(self: object) -> bool:
        try:
            if exists('Sounder files'):
                copytree(join(self.cwd, 'Build', 'dist', 'Sounder5'),
                         'Sounder files', dirs_exist_ok=True)
                return True
            return False
        except Exception as err_obj:
            self.__push_msg_(f'Error: {err_obj}', type='err')
            return False

    def __copy_folders(self: object) -> bool:
        try:
            move(join(self.cwd, 'Build', 'Resources'), 'Sounder files')
            remove(join('Sounder files', 'Resources',
                   'Icons', 'Updater', 'cat.gif'))
            remove(join('Sounder files', 'Resources',
                   'Icons', 'Updater', 'setup.ico'))
            move(join(self.cwd, 'Build', 'Components'), 'Sounder files')
            return True
        except Exception as err_obj:
            self.__push_msg_(f'Error: {err_obj}', type='err')
            return False

    def __clean_up(self: object) -> bool:
        try:
            if exists('Build'):
                rmtree('Build', ignore_errors=True)
                return True
            return False
        except Exception as err_obj:
            self.__push_msg_(f'Error: {err_obj}', type='err')
            return False

    #     push_info("\n\n" + str(grepexc.output))
    #     return False
    # for line in iter(shell.stdout.readline, b''):
    #     push_info(str(line.decode("utf-8")))
    # shell.wait()

    #         return True
    #     except Exception as err_obj:
    #         self.__push_msg_(f'Error: {err_obj}')
    #         return False


if __name__ == '__main__':
    Builder().mainloop()
