import os
from random import shuffle
from typing import Dict, List, Optional

from progressbar import progressbar

from config import RANDOMIZED_GROUP_SIZE
from utils import (choose_edition, choose_version, create_assets_json,
                   create_dir, generate_paths, load_json_data, permission)


def group_indices(edition_size: int,
                  group_size: int) -> List[List[str]]:
    temp = [str(i + 1) for i in range(edition_size)]
    shuffle(temp)

    groups = []
    while len(temp) > group_size:
        groups.append(list(temp.pop() for _ in range(group_size)))

    groups.append((temp))
    return groups


def move_single_image(img_path: str, group_index: str,
                      reverse : bool = False) -> None:
    target = img_path
    destination = os.path.join(os.path.dirname(img_path), 
                               f'group {group_index}',
                               os.path.basename(img_path))
    if reverse:
        target, destination = destination, target
    if os.path.exists(target):
        os.rename(target, destination)


def create_group_json(paths: Dict[str, str],  group_index: str,
                      indices: List[str]) -> None:
    all_data = load_json_data(paths['edition'])
    json_data = {k: v for k, v in all_data.items() if k in indices}
    create_assets_json(json_data, os.path.join(
        paths['images'], f'group {group_index}'))


def create_group(paths: Dict[str, str], group_index: str, indices: List[str],
                 edition_size: int, reverse: bool = False) -> None:
    if not reverse:
        create_dir(os.path.join(paths['images'], f'group {group_index}'))
        create_group_json(paths, group_index, indices)
    zfill_count = len(str(edition_size))
    for i in indices:
        image_name = str(i).zfill(zfill_count) + '.png'
        img_path = os.path.join(paths['images'], image_name)
        move_single_image(img_path, group_index, reverse)


def get_prev_randomized_indices(group: str, paths: Dict[str, str]):
    path = os.path.join(paths['images'], group)
    return [k for k in load_json_data(path).keys()]


def revert_groups(groups: List[str], paths: Dict[str, str],
                 edition_size: int) -> None:
    print('Reverting groups')
    indices = [get_prev_randomized_indices(group, paths) for group in groups]
    for i, group in progressbar(enumerate(indices, start=1)):
        create_group(paths, str(i), group, edition_size, reverse=True)
    print()

def create_random_groups(version_path: str, edition_name: Optional[str] = None,
                         group_size: int = RANDOMIZED_GROUP_SIZE) -> None:
    if edition_name is None:
        edition_name = choose_edition(version_path)

    if edition_name:
        paths = generate_paths(version_path, edition_name)
        edition_size = len(load_json_data(paths['edition']))
        if os.path.exists(paths['images']):
            groups = list(filter(lambda x: x.startswith('group'),
                            os.listdir(paths['images'])))
            if any(groups):
                if not permission(
                'Random groups already exist. Re-randomize'):
                    return None
                revert_groups(groups, paths, edition_size)
        zfill_count = len(str(edition_size // group_size + 1))
        indices = group_indices(edition_size, group_size)
        print('Creating groups')
        for i, group in progressbar(enumerate(indices, start=1)):
            create_group(paths, str(i).zfill(zfill_count), group, edition_size)
        print()


def randomized(version_path: str, path: str, edition_name: str) -> bool:
    try:
        if any(filter(lambda x: x.startswith('group '), os.listdir(path))):
            return True
    except FileNotFoundError:
        if permission('Create randomized groups'):
            create_random_groups(version_path, edition_name)
            return True
        return False


if __name__ == '__main__':
    create_random_groups(choose_version())
    print('Task complete!')
