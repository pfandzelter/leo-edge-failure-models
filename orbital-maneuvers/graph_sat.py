#!/usr/bin/env python3
#
# Usage: graph_sat.py <input-files> <output-dir>
#

import glob
import os
import sys
import multiprocessing as mp
import functools

import pandas as pd
# import matplotlib as mpl
import matplotlib.pyplot as plt
# import matplotlib.animation as animation
import seaborn as sns
import tqdm


def _graph_sat_trajectory(input_file: str, output_dir: str) -> None:

    cmap = sns.color_palette("crest", as_cmap=True)

    # sat name is file name without extension and directory
    sat_name = os.path.basename(input_file).split(".")[0]

    # create output file name
    output_file = os.path.join(output_dir, sat_name + ".png")

    # read data
    df = pd.read_csv(input_file)

    # create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # create figure
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # timestamps = df['date'].astype('datetime64[ns]').values
    # min_timestamp = timestamps.min()
    # max_timestamp = timestamps.max()
    # timestamp_range = max_timestamp - min_timestamp
    # colors = [cmap((x - min_timestamp) / timestamp_range) for x in timestamps]

    # make a color map based on distance from the baseline
    # min color is 0, max color is 10000m
    colors = [cmap(x / 10000) for x in df['distance_baseline']]

    ax.scatter(df['x'], df['y'], df['z'], color=colors, marker="x", s=1)

    time_text = ax.text2D(-.1, .1, f"max distance {max(df['distance_baseline'])}", fontsize=15)

    # ax.scatter(df['x_baseline'], df['y_baseline'], df['z_baseline'], color="r", marker=".", s=0.1)

    # save figure
    plt.savefig(output_file, dpi=300)
    plt.close(fig)


if __name__ == "__main__":

    # parse arguments

    if len(sys.argv) < 3:
        print("Usage: graph_sat.py <input-files> <output-dir>")
        sys.exit(1)

    input_files = sys.argv[1]
    output_dir = sys.argv[2]

    # find all files with the given prefix
    with mp.Pool() as pool:
        files = glob.glob(input_files + "*")

        r = list(tqdm.tqdm(pool.imap_unordered(functools.partial(_graph_sat_trajectory, output_dir=output_dir), files, chunksize=10), total=len(files)))

        pool.close()
        pool.join()
