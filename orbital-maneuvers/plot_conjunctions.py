#!/usr/bin/env python3
#
# Convert archived TLE data to CSV for further analysis
#
# Usage: plot_conjunctions.py <input-conjunctions-file-prefix> <input-tle-file-prefix> <output-file-prefix>
#

# for each satellite, plot its altitude over time
# if a conjunction is reported, also plot it
# any correlation?

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

# only recorded conjunctions after this date
start_date = "2023-01-06"

def _graph_sat_altitude(input_file: str, input_conjunctions_file_prefix: str, output_dir: str):

    # sat name is file name without extension and directory
    sat_name = os.path.basename(input_file).split(".")[0]

    # read conjunctions
    conjunction_file = input_conjunctions_file_prefix + f"{sat_name}.csv"

    try:
        conjunctions = pd.read_csv(conjunction_file)
    except:
        print(f"Could not read conjunctions for {sat_name} (file exists: {os.path.exists(conjunction_file)})")
        return

    conjunctions['date'] = pd.to_datetime(conjunctions['date'])
    conjunctions['date_tca'] = pd.to_datetime(conjunctions['date_tca'])

    important_conjunctions = conjunctions[conjunctions['probability'] > 10e-4]

    if len(important_conjunctions) == 0:
        # print(f"No important conjunctions for {sat_name}")
        return

    # # filter conjunctions for this satellite
    # conjunctions = conjunctions[(conjunctions['name1'] == sat_name) | (conjunctions['name2'] == sat_name)]

    # read input file
    df = pd.read_csv(input_file)
    df = df[df['date'] >= start_date]
    df['date'] = pd.to_datetime(df['date'])

    # create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # create figure
    g = sns.lineplot(data=df, x="date", y="distance_ground", color="#4477AA", errorbar=None)
    # sns.lineplot(data=df, x="date", y="distance_baseline_ground", color="#EE6677", label="baseline", ax=g)

    # plot conjunctions
    for index, row in conjunctions.iterrows():
        important = row["probability"] > 10e-4
        g.axvline(x=row['date_tca'], color="#EE6677" if important else "#228833", linestyle="-" if important else "--", linewidth=0.5 if important else 0.05)

    g2 = g.twinx()
    sns.scatterplot(x=important_conjunctions['date_tca'], y=important_conjunctions['probability'], color="#EE6677", size=important_conjunctions["probability"], ax=g2, legend=False)
    g2.set_yscale("log")

    # save figure
    plt.savefig(os.path.join(output_dir, sat_name + ".png"), dpi=100, bbox_inches="tight")
    plt.close(g.get_figure())

    del df
    del important_conjunctions
    del conjunctions

    return

if __name__ == "__main__":

    # parse arguments

    if len(sys.argv) < 3:
        print("Usage: plot_conjunctions.py <input-conjunctions-file-prefix> <input-tle-file-prefix> <output-file-prefix>")
        sys.exit(1)

    input_conjunctions_file_prefix = sys.argv[1]
    input_tle_file_prefix = sys.argv[2]
    output_dir = sys.argv[3]

    max_workers = mp.cpu_count() - 1
    # max_workers = 1

    # find all files with the given prefix
    with mp.Pool(processes=max_workers) as pool:
        files = glob.glob(input_tle_file_prefix + "*")

        r = list(tqdm.tqdm(pool.imap_unordered(functools.partial(_graph_sat_altitude, input_conjunctions_file_prefix=input_conjunctions_file_prefix, output_dir=output_dir), files, chunksize=10), total=len(files)))

        pool.close()
        pool.join()
