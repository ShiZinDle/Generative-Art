import os
from typing import Optional

import matplotlib.pyplot as plt

from utils import choose_edition, choose_version, generate_paths

def draw_graph(version_path: Optional[str] = None,
               edition_name: Optional[str] = None) -> None:
    if version_path is None:
        version_path = choose_version()
    
    if version_path:
        if edition_name is None:
            edition_name = choose_edition(version_path)

        if edition_name:
            paths = generate_paths(version_path, edition_name)
            path = os.path.join(paths['edition'], 'score.txt')

            with open(path, 'r') as file:
                y = sorted(float(line.rstrip()) for line in file.readlines())

            x = range(len(y))
            # plotting the points
            plt.plot(x, y)

            # naming the x axis
            plt.xlabel('Asset #')
            # naming the y axis
            plt.ylabel('Rarity Score')

            # giving a title to my graph
            plt.title('Rarity Score')

            # function to show the plot
            plt.show()


if __name__ == '__main__':
    draw_graph()