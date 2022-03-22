import csv
import json
import os
from shutil import rmtree
from typing import Callable, Dict, List, Union

from config import RARITY_TABLE_PATH

CONFIG_DICT = List[Dict[str, Union[int, str, List[int]]]]
PNG = -1 * len('.png')

# Get file paths based on edition
def generate_paths(version_path: str, edition_name: str) -> Dict[str, str]:
    edition_path = os.path.join(version_path, 'output',
                                'edition ' + str(edition_name))
    images_path = os.path.join(edition_path, 'images')
    csv_path = os.path.join(edition_path, 'assets.csv')
    json_path = os.path.join(edition_path, 'assets.json')
    metadata_path = os.path.join(edition_path, 'metadata')
    

    return {'edition': edition_path,
            'images': images_path,
            'csv': csv_path,
            'json': json_path,
            'metadata': metadata_path}


def create_dir(path: str) -> None:
    # Create output directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)


def erase_dir(path: str) -> None:
    rmtree(path)


def erase_edition(version_path: str, edition_name: str) -> None:
    print('Erasing edition...\n')
    erase_dir(generate_paths(version_path, edition_name)['edition'])


def get_dirs(path: str) -> Dict[str, str]:
    try:
        dirs = {str(i): file for i, file
                in enumerate(os.listdir(path), start=1)
                if os.path.isdir(os.path.join(path, file))}
    except FileNotFoundError:
        return {}
    return dirs


def get_version_dirs(path: str) -> Dict[str, str]:
    return {str(i): v for i, v in enumerate(
        [v for v in get_dirs(path).values()
         if v != os.path.basename(os.getcwd())], start=1)}


def get_edition_dirs(version_path: str) -> Dict[str, str]:
    return {k: v[len('edition '):]
            for k, v in get_dirs(os.path.join(version_path, 'output')).items()
            if v.startswith('edition')}


def choose_dir(path: str, desc: str,
               dir_list_func: Callable = get_dirs) -> str:
    response = ''
    dirs = dir_list_func(path)
    if dirs:
        print(f'Choose {desc} (by number):')
        for i, directory in dirs.items():
            print(i, directory)
        while response not in dirs.keys():
            response = input()
        print()
        return dirs[response]

    return response


def choose_version() -> str:
    version = choose_dir(os.path.dirname(os.getcwd()),
                         'version', get_version_dirs)
    if not version:
        print("Oops! Looks like there are no existing versions!\n")
    return os.path.join(os.path.dirname(os.getcwd()), version)


def choose_edition(version_path: str) -> str:
    edition = choose_dir(version_path, 'edition', get_edition_dirs)
    if not edition:
        print("Oops! Looks like there are no editions for this version!\n")
    return edition


def permission(message: str) -> bool:
    print(f"{message}? (y/n)")
    response = ''
    while response not in ('y', 'n'):
        response = input().lower()
    print()
    return response == 'y'


def load_json_data(path: str) -> Dict[str, List[str]]:
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print('Edition data does not exist.')
        return {}


def choose_mode(path: str) -> str:
    if os.path.exists(path):
        return 'w'
    return 'x'


def create_assets_json(json_data: List[List[str]], path: str) -> None:
    with open(path, choose_mode(path)) as file:
        json.dump(json_data, file)


def create_csv(rows: List[str], path: str) -> None:
    with open(path, choose_mode(path), newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def zip_layers(path: str) -> List[List[str]]:
    with open(path, 'r') as file:
        reader = csv.reader(file)
        return zip(*[row for row in reader])


def parse_rarities(rarities: List[str]) -> List[int]:
    placeholder = 1
    if any(filter(lambda x: x != '-', rarities)):
        placeholder = 0
    return [int(trait) if trait != '-' else placeholder for trait in rarities]


def extract_rarity_from_csv(version_path: str) -> CONFIG_DICT:
    path = os.path.join(version_path, RARITY_TABLE_PATH)
    cols = zip_layers(path)
    percentage = []
    for i, col in enumerate(cols):
        if i % 4 == 0:
            layer = {}
        if i % 4 == 1:
            layer['name'], layer['id'] = col[0], int(col[1])
            none_index = col.index('None')
        elif i % 4 == 2:
            layer['rarity_weights'] = parse_rarities(col[2:none_index])
            none_percent = int(col[none_index])
            if none_percent:
                layer['rarity_weights'].insert(0, none_percent)
            percentage.append(layer)
    return sorted(percentage, key=lambda x: x['id'])


def extract_prev_data(version_path: str,
                      edition_name: str) -> List[List[List[str]]]:
    paths = generate_paths(version_path, edition_name)
    json_data = [v for v in load_json_data(paths['json']).values()]
    with open(paths['csv'], 'r') as file:
        csv_data = [row[1:] for row in list(csv.reader(file))[1:]]
    return list(zip(csv_data, json_data))
