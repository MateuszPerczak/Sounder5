from os.path import join, abspath
from os import listdir, remove
from PIL import Image
from PIL.ImageOps import invert
from typing import ClassVar


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


from_path: str = 'Resources\\Icons\\Light'
to_path: str = 'Resources\\Icons\\Dark'

# remove unnecessary files
files: list = listdir(from_path)
printProgressBar(0, len(files) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
for file in listdir(to_path):
    if file in files:
        continue
    else:
        remove(abspath(join(to_path, file)))
# remove files list
ignore_files: tuple = ()
# invert colors of icons
for icon in files:
    printProgressBar(files.index(icon), len(files) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    if icon in ignore_files: continue
    image: ClassVar = Image.open(join(from_path, icon))
    if image.mode == 'RGBA':
        red: ClassVar; green: ClassVar; blue: ClassVar; alpha: ClassVar
        red, green, blue, alpha = image.split()
        del image
        # inverted image
        temp_icon: ClassVar = Image.merge('RGB', (red, green, blue))
        inverted_image: ClassVar = invert(temp_icon)
        del temp_icon
        # get RGB values of inverted image
        red, green, blue = inverted_image.split()
        del inverted_image
        new_image: ClassVar = Image.merge('RGBA', (red, green, blue, alpha))
        # save new image to new dir
        new_image.save(join(to_path, icon))
        del new_image, red, green, blue, alpha

