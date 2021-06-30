try:
    from python_minifier import minify
    from os import system, mkdir, remove, getcwd
    from os.path import exists, basename, join
except ImportError as err_obj:
    exit(err_obj)

current_dir = getcwd()

# prepare files to minify

files_to_minify: tuple = ('Sounder5.py', 'Updater.py', 'Components\\Setup.py', 'Components\\SongMenu.py', 'Components\\SystemTheme.py', 'Components\\DirWatcher.py')

# prepare folder for minified files
if not exists('build'):
    mkdir('build')
    mkdir('build\\Components')
# minify all
for file in files_to_minify:
    minified_content: str = ''
    with open(file, 'r') as data:
        minified_content = minify(data.read()) # , rename_globals=True, rename_locals=True, hoist_literals=True
    if minified_content:
        with open(f'build\\{file}', 'w') as data:
            data.write(minified_content)

