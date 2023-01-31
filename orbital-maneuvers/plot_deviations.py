#!/usr/bin/env python3
#
# Convert archived TLE data to CSV for further analysis
#
# Usage: plot_deviations.py <input-conjunctions-file-prefix> <input-tle-file-prefix> <output-file-prefix>
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

# only recorded conjunctions after this date
start_date = "2023-01-06"
end_date = "2023-01-20"
high_risk = 10e-4

if __name__ == "__main__":

    # parse arguments

    if len(sys.argv) < 3:
        print("Usage: plot_deviations.py <input-conjunctions-file-prefix> <input-tle-file-prefix> <output-file-prefix>")
        sys.exit(1)

    input_conjunctions_file_prefix = sys.argv[1]
    input_tle_file_prefix = sys.argv[2]
    output_dir = sys.argv[3]

    max_workers = mp.cpu_count() - 1
    # max_workers = 1

    # find all files with the given prefix
    files = glob.glob(input_tle_file_prefix + "*")

    # create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conjuncted_satellites = set()

    for f in tqdm.tqdm(files, desc="Finding conjuncted satellites"):
        sat_name = os.path.basename(f).split(".")[0]

        # read conjunctions
        conjunction_file = input_conjunctions_file_prefix + f"{sat_name}.csv"

        try:
            conjunctions = pd.read_csv(conjunction_file)
        except:
            print(f"Could not read conjunctions for {sat_name} (file exists: {os.path.exists(conjunction_file)})")
            continue

        conjunctions = conjunctions[conjunctions['date'] >= start_date]
        conjunctions = conjunctions[conjunctions['date'] <= end_date]

        conjunctions['date'] = pd.to_datetime(conjunctions['date'])
        conjunctions['date_tca'] = pd.to_datetime(conjunctions['date_tca'])

        important_conjunctions = conjunctions[conjunctions['probability'] > high_risk]

        if len(important_conjunctions) == 0:
            # print(f"No important conjunctions for {sat_name}")
            continue

        conjuncted_satellites.add(sat_name)

    # next, plot distance distribution for all the satellites
    distances = []

    for f in tqdm.tqdm(files, desc="Getting altitude"):
        sat_name = os.path.basename(f).split(".")[0]

        if not sat_name in conjuncted_satellites:
            continue

        # read input file
        sat_df = pd.read_csv(f)
        sat_df = sat_df[sat_df['date'] >= start_date]
        sat_df['date'] = pd.to_datetime(sat_df['date'])

        df_distance = sat_df[["distance_ground"]].copy()
        df_distance["satellite"] = sat_name

        distances.append(df_distance)

    df = pd.concat(distances)
    df.rename(columns={"distance_ground": "altitude"}, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # now plot!
    g = sns.violinplot(data=df, x="satellite", y="altitude", color="#4477AA")
    g.set_xticklabels(g.get_xticklabels(), rotation=90)

    # save figure
    plt.savefig(os.path.join(output_dir, "altitude_distribution.png"), dpi=100, bbox_inches="tight")
    plt.close(g.get_figure())
