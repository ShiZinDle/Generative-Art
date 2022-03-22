import os
import random
from typing import Dict, List, Union
import warnings

import numpy as np
from progressbar import ProgressBar

from config import ASSETS_PATH
from utils import (choose_version, CONFIG_DICT, create_csv, create_dir,
                   create_assets_json, erase_edition, extract_rarity_from_csv,
                   generate_paths, permission, PNG)


warnings.simplefilter(action='ignore', category=FutureWarning)


# Weight rarities and return a numpy array that sums up to 1
def get_weighted_rarities(arr):
    return np.array(arr) / sum(arr)


# Parse the configuration file and make sure it's valid
def parse_config(
    version_path: str) -> List[Dict[str, Union[int, str, List[int]]]]:
    edition_config = extract_rarity_from_csv(version_path)
    # Loop through all layers defined in CONFIG
    for layer in edition_config:

        # Go into assets/ to look for layer folders
        layer_path = os.path.join(version_path, ASSETS_PATH, layer['name'])

        # Generate final rarity weights
        # if layer['rarity_weights'] is None:
        #     rarities = [1 for _ in traits]
        # elif layer['rarity_weights'] == 'random':
        #     rarities = [random.random() for _ in traits]
        # elif type(layer['rarity_weights'] == 'list'):

        # Re-assign final values to main CONFIG
        # Get trait array in sorted order
        layer['traits'] = sorted([trait[:PNG] for trait
                                  in os.listdir(layer_path)
                                  if trait[0] != '.'])

        if len(layer['traits']) == len(layer['rarity_weights']) - 1:
            # msg = 'Rarity weights are invalid.'
            # msg += ' Make sure you have the correct number of rarity weights'
            # raise ValueError(msg)
            layer['traits'].insert(0, None)

        layer['rarity_weights'] = get_weighted_rarities(
            layer['rarity_weights'])
        layer['cum_rarity_weights'] = np.cumsum(layer['rarity_weights'])

    return edition_config


# Get total number of distinct possible combinations
def get_total_combinations(edition_config: CONFIG_DICT) -> int:
    total = 1
    for layer in edition_config:
        total = total * len(layer['traits'])
    return total


# Select an index based on rarity weights
def select_index(cum_rarities, rand):
    cum_rarities = [0] + list(cum_rarities)
    for i in range(len(cum_rarities) - 1):
        if rand >= cum_rarities[i] and rand <= cum_rarities[i+1]:
            return i

    # Should not reach here if everything works okay
    return None


# Generate a set of traits given rarities
def generate_trait_set_from_config(edition_config: CONFIG_DICT,
                                   version_path: str) -> List[List[str]]:
    trait_set = []
    trait_paths = []

    for layer in edition_config:
        # Extract list of traits and cumulative rarity weights
        traits, cum_rarities = layer['traits'], layer['cum_rarity_weights']

        # Generate a random number
        rand_num = random.random()

        # Select an element index
        # based on random number and cumulative rarity weights
        idx = select_index(cum_rarities, rand_num)

        # Add selected trait to trait set
        trait_set.append(traits[idx])
        for i, trait in enumerate(trait_set):
            if trait is None:
                trait_set[i] = 'none'

        # Add trait path to trait paths if the trait has been selected
        if traits[idx] is not None:
            trait_path = os.path.join(version_path, ASSETS_PATH,
                                      layer['name'], f'{traits[idx]}.png')
            trait_paths.append(trait_path)

    return [trait_set, trait_paths]


def validate_traits(trait_set: List[str]) -> bool:
    if trait_set[5] == 'Yellow' and trait_set[4] == 'Yellow':
        return False
    if (trait_set[1] in ('Black', 'Red')
        and trait_set[3] not in ('Black', 'Face', 'Sad')):
        return False
    return True


# Generate the image set.
def generate_asset_data(
    version_path:str, edition_config: CONFIG_DICT, count: int,
    all_data: List[List[List[str]]] = []) -> List[List[List[str]]]:

    bar = ProgressBar(max_value=count).start()
    i = 0

    # Create the images data
    while len(all_data) < count:
        # Get a random set of valid traits based on rarity weights
        traits = generate_trait_set_from_config(edition_config, version_path)
        if traits not in all_data and validate_traits(traits[0]):
            all_data.append(traits)
            i += 1
            bar.update(i)

    bar.update(count)
    print()
    return all_data


def create_csv_data(edition_config: CONFIG_DICT,
                    csv_data: List[List[str]]) -> List[str]:
    header = ['']
    for layer in edition_config:
        header.append(layer['name'].title())

    metadata = [[i + 1] + t for i, t in enumerate(csv_data)]
    metadata.insert(0, header)
    return metadata


def choose_edition_name(version_path: str) -> str:
    msg = '\nAn edition with the chosen name already exists.'
    msg += ' Continue and erase previous edition'
    print('What would you like to call this edition?')
    while True:
        name = input().strip()
        if f'edition {name}' in os.listdir(
            os.path.join(version_path, 'output')):
            if permission(msg):
                erase_edition(version_path, name)
                return name
            else:
                print('Please choose a new name:')
        else:
            return name


# Main function. Point of entry
def create_edition_data(version_path: str, edition_name: str = '',
                        prev_data: List[List[List[str]]] = []) -> str:
    if not edition_name:
        edition_name = choose_edition_name(version_path)

    print('Checking assets...')
    edition_config = parse_config(version_path)
    print('Assets look great! We are good to go!\n')

    total_combos = get_total_combinations(edition_config)
    print(f'You can create a total of {total_combos} distinct avatars')

    msg1 = msg2 = ''
    if prev_data:
        existing_amount = len(prev_data)
        msg1 = f'{existing_amount} avatars already exist\n'
        msg2 = 'additional '
        total_combos -= existing_amount
    msg = f'{msg1}How many {msg2}avatars would you like to create?'
    msg += f' Enter a number greater than 0 and smaller than {total_combos}:'
    print(msg)
    num_avatars = -1
    while num_avatars <= 0 <= total_combos:
        try:
            num_avatars = int(input())
        except ValueError:
            continue
    if prev_data:
        num_avatars += existing_amount
    print()

    paths = generate_paths(version_path, edition_name)

    print('\nStarting task...')

    print('\nCreating directory...')
    create_dir(paths['edition'])

    print('\nGenerating image data...')
    all_data = generate_asset_data(version_path, edition_config,
                                   num_avatars, prev_data)
    csv_data = [data[0] for data in all_data]
    json_data = {i + 1: data for i, data
                 in enumerate([data[1] for data in all_data])}

    print('\nCreating trait rarity table...\n')
    create_csv(create_csv_data(edition_config, csv_data), paths['csv'])
    create_assets_json(json_data, paths['json'])

    return edition_name


if __name__ == '__main__':
    create_edition_data(choose_version())
    print('Task complete!')
