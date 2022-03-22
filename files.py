import os

from utils import choose_version


def rename_files(version_path: str) -> None:
    path = os.path.join(version_path, 'assets')
    for directory in os.listdir(path):
        dir_path = os.path.join(path, directory)
        files = os.listdir(dir_path)
        z = len(str(len(files)))
        i = 1
        for file in files:
            filename = os.path.join(dir_path, file)
            if file.startswith('.'):
                os.remove(filename)
            else:
                newname = os.path.join(dir_path, f'{directory}-{str(i).zfill(z)}.png')
                os.rename(filename, newname)
                i += 1


if __name__ == '__main__':
    rename_files(choose_version())
    print('Task complete!')
