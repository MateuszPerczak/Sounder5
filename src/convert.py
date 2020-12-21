from os.path import join, abspath
from os import listdir, remove
from PIL import Image
from PIL.ImageOps import invert
from typing import ClassVar


from_path: str = 'Resources\\Icons\\Light'
to_path: str = 'Resources\\Icons\\Dark'

# remove unnecessary files
files: list = listdir(from_path)
for file in listdir(to_path):
    if file in files:
        continue
    else:
        print(f'Deleted {file}!')
        remove(abspath(join(to_path, file)))
# remove files list
del files
ignore_files: tuple = ()

# invert colors of icons
for icon in listdir(from_path):
    if icon in ignore_files: continue
    image: ClassVar = Image.open(join(from_path, icon))
    if image.mode == 'RGBA':
        print(f'Converting file {icon}!')
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
    else:
        print(f'Cannot convert file {icon}!')

print('Done!')