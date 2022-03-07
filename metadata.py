from copy import deepcopy
import json
import os
from typing import Optional
import warnings

import pandas as pd
from progressbar import progressbar

from config import BASE_JSON
from utils import choose_edition, choose_version, create_dir, generate_paths


warnings.simplefilter(action='ignore', category=FutureWarning)

# Function to convert snake case to sentence case
def clean_attributes(attr_name: str) -> str:
    return ' '.join(word.title() if word.isupper() or word.islower() else word
                    for word in attr_name.replace('_', ' ').split())


# Function to get attribute metadata
def get_attribute_metadata(csv_path):
    # Read attribute data from metadata file 
    df = pd.read_csv(csv_path)
    df = df.drop('Unnamed: 0', axis = 1)
    df.columns = [clean_attributes(col) for col in df.columns]

    # Get zfill count based on number of images generated
    zfill_count = len(str(df.shape[0]))

    return df, zfill_count


# Main function that generates the JSON metadata
def create_metadata_files(version_path: str,
                          edition_name: Optional[str] = None) -> None:
    if edition_name is None:
        edition_name = choose_edition(version_path)

    if edition_name:
        paths = generate_paths(version_path, edition_name)

        # Make json folder
        create_dir(paths['json'])
        # Get attribute data and zfill count
        df, zfill_count = get_attribute_metadata(paths['csv'])

        print('Creating metadata files.')
        for idx, row in progressbar(df.iterrows()):
            # Get a copy of the base JSON (python dict)
            item_json = deepcopy(BASE_JSON)
            # Append number to base name
            item_json['name'] = item_json['name'] + str(idx)
            # Append image PNG file name to base image path
            item_json['image'] = (item_json['image'] + '/'
                                  + str(idx).zfill(zfill_count) + '.png')
            # Convert pandas series to dictionary
            attr_dict = dict(row)
            # Add all existing traits to attributes dictionary
            for attr in attr_dict:
                if attr_dict[attr] != 'none':
                    item_json['attributes'].append({ 'trait_type': attr,
                                                    'value': attr_dict[attr] })
            # Write file to json folder
            item_json_path = os.path.join(paths['json'],
                                          str(idx + 1) + '.json')
            with open(item_json_path, 'w') as f:
                json.dump(item_json, f)

if __name__ == '__main__':
    create_metadata_files(choose_version())
    print('Task complete!')
