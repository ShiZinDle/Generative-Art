import os

PATH = f'D:\Yuval\Game Design\My Inch Island\Generative Art\Totem\Assets'

for directory in os.listdir(PATH):
    dir_path = os.path.join(PATH, directory)
    files = os.listdir(dir_path)
    z = len(str(len(files)))
    for i, file in enumerate(files, start=1):
        filename = os.path.join(dir_path, file)
        newname = os.path.join(dir_path, f'{directory}-{str(i).zfill(z)}.png')
        os.rename(filename, newname)