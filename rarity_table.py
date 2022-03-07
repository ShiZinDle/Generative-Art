import os
from typing import List

from config import ASSETS_PATH, RARITY_BY_PERCENTAGE
from utils import choose_version, create_csv, PNG


def get_layers(version_path: str) -> List[str]:
    return os.listdir(os.path.join(version_path, ASSETS_PATH))


def create_headers(layers: List[str]) -> List[str]:
    header = []
    ids = []
    for layer in layers:
        header.extend(['-', layer.title(), 'Rarity Weight', '-'])
        ids.extend(['id', '0', '-', '-'])
    return [header, ids]


def get_layer_traits(version_path: str, layer_name: str) -> List[str]:
    return [trait[:PNG] for trait in
            os.listdir(os.path.join(version_path, ASSETS_PATH, layer_name))]


def get_all_traits(version_path: str, layers: List[str]) -> List[List[str]]:
    return [get_layer_traits(version_path, layer) for layer in layers]


def get_col(n: int) -> str:
    order = ord('C') + n * 4
    if order <= 90:
        return chr(order)
    return 'A' + chr(order - 26)


def create_table_rows(version_path: str) -> List[str]:
    layers = get_layers(version_path)
    traits = get_all_traits(version_path, layers)
    num_rows = max(map(len, traits)) + 2
    rows = create_headers(layers)
    filler = '-' if RARITY_BY_PERCENTAGE else ''
    for i in range(num_rows):
        row = []
        for n, layer in enumerate(traits):
            if i < len(layer):
                row.extend([i + 1, layer[i], '-', '-'])
            elif i == len(layer):
                row.extend([i + 1, 'None', '0', '-'])
            elif i == num_rows - 1 and RARITY_BY_PERCENTAGE:
                col = get_col(n)
                row.extend(['-', 'Total', f'=SUM({col}2:{col}{i + 1})', '-'])
            else:
                row.extend([filler, filler,filler, filler])
        rows.append(row)
    return rows


def create_rarity_table(version_path: str) -> None:
    create_csv(create_table_rows(version_path),
               os.path.join(version_path, 'rarity table.csv'))


if __name__ == '__main__':
    print('Creating rarity table.')
    create_rarity_table(choose_version())
    print('Task complete!')
