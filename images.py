import os
from sys import argv
import time
from typing import Optional

from PIL import Image
from progressbar import progressbar

from randomizer import randomized
from utils import (choose_dir, choose_edition, choose_version, create_dir,
                   generate_paths, load_json_data, permission)


# Generate a single image given an array of filepaths representing layers
def generate_single_image(filepaths, output_filename=None):
    # Treat the first layer as the background
    bg = Image.open(os.path.join('assets', filepaths[0]))

    # Loop through layers 1 to n and stack them on top of another
    for filepath in filepaths[1:]:
        if filepath.endswith('.png'):
            img = Image.open(os.path.join('assets', filepath))
            bg.paste(img, (0,0), img)

    # Save the final image into desired location
    if output_filename is not None:
        bg.save(output_filename)
    else:
        # If output filename is not specified,
        # use timestamp to name the image and save it in output/single_images
        if not os.path.exists(os.path.join('output', 'single_images')):
            os.makedirs(os.path.join('output', 'single_images'))
        bg.save(os.path.join('output', 'single_images',
                             str(int(time.time())) + '.png'))


def get_edition_name_to_print(img_dir: str) -> str:
    basename = os.path.basename(img_dir)
    dirname = os.path.dirname(img_dir)
    if basename.lower() == 'images':
        return os.path.basename(dirname)[len("edition "):]
    return f'{get_edition_name_to_print(dirname)}: {basename}'


def generate_images(json_dir_path: str, img_dir: str,
                    zfill_count: int) -> None:
    all_data = load_json_data(json_dir_path)
    if all_data:
        create_dir(img_dir)
        edition_name = get_edition_name_to_print(img_dir)
        print(f'Generating {edition_name} images')
        # Will require this to name final images as 000, 001,...
        for i, data in progressbar(all_data.items()):
            # Set image name
            image_name = i.zfill(zfill_count) + '.png'

            img_path = os.path.join(img_dir, image_name)
            if not os.path.exists(img_path):
                # Generate the actual image
                generate_single_image(data, img_path)
        print()


def images_main(version_path: str, edition_name: Optional[str] = None) -> None:
    if edition_name is None:
        edition_name = choose_edition(version_path)

    paths = generate_paths(version_path, edition_name)
    all_data = load_json_data(paths['edition'])
    zfill_count = len(str(len(all_data.keys())))

    if randomized(version_path, paths['images'], edition_name):
        if permission('Create images for all groups'):
            for d in os.listdir(paths['images']):
                dir_path = os.path.join(paths['images'], d)
                generate_images(dir_path, dir_path, zfill_count)
        else:
            dir_path = os.path.join(paths['images'],
                                    choose_dir(paths['images'], 'group'))
            generate_images(dir_path, dir_path, zfill_count)
    else:
        generate_images(paths['edition'], paths['images'], zfill_count)


if __name__ == '__main__':
    try:
        images_main(argv[1])
    except (FileNotFoundError, IndexError):
        images_main(choose_version())
    finally:
        print('Task complete!')
