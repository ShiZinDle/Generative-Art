import os
from assets import create_edition_data
from images import all_images_exist, images_main
from metadata import create_metadata_files
from randomizer import create_random_groups
from utils import (choose_edition, choose_version, create_dir,
                   extract_prev_data, get_edition_dirs, permission)

def main():
    version_path = choose_version()
    create_dir(os.path.join(version_path, 'output'))
    editions = get_edition_dirs(version_path)
    if (not editions or permission('Create a new edition')):
        edition_name = create_edition_data(version_path)
    else:
        edition_name = choose_edition(version_path)

    if edition_name:
        prev_data = extract_prev_data(version_path, edition_name)
        if all_images_exist(version_path, edition_name, prev_data):
            create_edition_data(version_path, edition_name, prev_data)
        if permission('Create images'):
            images_main(version_path, edition_name)
            print("Task complete!\n")
        else:
            if permission('Create randomized groups'):
                create_random_groups(version_path, edition_name)

        if permission('Create metadata files'):
            create_metadata_files(version_path, edition_name)
            print('Task complete!')


if __name__ == '__main__':
    main()
