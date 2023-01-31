#!/usr/bin/env python3
#
# Usage: propagate_sat.py <input-file> <output-dir>
#

import os
import sys
import multiprocessing as mp
import functools

import pandas as pd
import sgp4.api as sgp4
import tqdm
import numpy as np

TIME_INTERVAL_MS = 60000

def _propagate(start_time, end_time, output_dir, arg):
    # sat_df = orig_data[orig_data["name"] == sat]
    # sat_df = sat_dfs[sat]
    # sat_df = sat_df
    sat_df, sat = arg

    sat_output = os.path.join(output_dir, f"{sat}.csv")

    # create a new dataframe with the interpolated values
    new_data = pd.DataFrame(
        {
            "date": pd.date_range(
                start=start_time, end=end_time, freq=f"{TIME_INTERVAL_MS}ms"
            )
        }
    )

    new_data["date"] = new_data["date"].astype("datetime64[ns]")

    sat_df.sort_values(by="date", inplace=True)
    sat_df.reset_index(drop=True, inplace=True)

    new_data.sort_values(by="date", inplace=True)
    new_data.reset_index(drop=True, inplace=True)

    # interpolate the values
    # print(new_data.dtypes)
    # print(sat_df.dtypes)
    new_data = pd.merge_asof(new_data, sat_df, on="date")
    # print(new_data.head())

    # additionally, get the baseline values (first row)
    # get the first row of the dataframe
    line1_baseline = sat_df.iloc[0]["line1"]
    line2_baseline = sat_df.iloc[0]["line2"]

    def _to_xyz(target_time, line1, line2):
        try:
            sat = sgp4.Satrec.twoline2rv(line1, line2)
        except Exception as e:
            # nothing to do here
            # just assume it is dead
            return 0, 0, 0

        # convert target time to Julian date
        jd, fr = sgp4.jday(target_time.year, target_time.month, target_time.day,
                            target_time.hour, target_time.minute, target_time.second + target_time.microsecond * 1e-6)

        # propagate to the given time
        e, r, d = sat.sgp4(jd, fr)

        return r[0] * 1000, r[1] * 1000, r[2] * 1000

    def _to_xyz_baseline(target_times, line1, line2):

        sat = sgp4.Satrec.twoline2rv(line1, line2)

        # propagate to the given time

        dates = [sgp4.jday(target_time.year, target_time.month, target_time.day, target_time.hour, target_time.minute, target_time.second + target_time.microsecond * 1e-6) for target_time in target_times]

        jd = np.array([d[0] for d in dates])
        fr = np.array([d[1] for d in dates])

        es, rs, ds = sat.sgp4_array(jd, fr)

        return rs[:, 0] * 1000, rs[:, 1] * 1000, rs[:, 2] * 1000

    # write to output file
    new_data[["x", "y", "z"]] = new_data.apply(lambda x: _to_xyz(x["date"], x["line1"], x["line2"]), axis=1, result_type="expand")

    # new_data[["x_baseline", "y_baseline", "z_baseline"]] = _to_xyz_baseline(new_data["date"], line1_baseline, line2_baseline)

    baseline_xyz = _to_xyz_baseline(new_data["date"], line1_baseline, line2_baseline)

    new_data["x_baseline"] = baseline_xyz[0]
    new_data["y_baseline"] = baseline_xyz[1]
    new_data["z_baseline"] = baseline_xyz[2]

    # distance between the satellite and the baseline in meters
    new_data["distance_baseline"] = np.sqrt((new_data["x"] - new_data["x_baseline"]) ** 2 + (new_data["y"] - new_data["y_baseline"]) ** 2 + (new_data["z"] - new_data["z_baseline"]) ** 2)

    # distance between the satellite and ground in meters
    new_data["distance_ground"] = np.sqrt(new_data["x"] ** 2 + new_data["y"] ** 2 + new_data["z"] ** 2) - 6371000

    # distance between the satellite baseline and ground in meters
    new_data["distance_baseline_ground"] = np.sqrt(new_data["x_baseline"] ** 2 + new_data["y_baseline"] ** 2 + new_data["z_baseline"] ** 2) - 6371000

    new_data[["date", "name", "x", "y", "z", "x_baseline", "y_baseline", "z_baseline", "distance_baseline", "distance_ground", "distance_baseline_ground"]].to_csv(sat_output, index=False)
    # new_data.to_csv(sat_output, index=False)
    # print(sat_output)
    # exit(1)

if __name__ == "__main__":
    # parse arguments

    if len(sys.argv) != 3:
        print("Usage: propagate_sat.py <input-file> <output-dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    # read input file
    orig_data = pd.read_csv(input_file)

    # interpolate at a given time interval
    start_time = orig_data["date"].min()
    end_time = orig_data["date"].max()

    orig_data["date"] = pd.to_datetime(orig_data["date"]).astype("datetime64[ns]")
    orig_data["old_date"] = orig_data["date"].copy()

    with mp.Pool() as pool:
        sats = list(orig_data["name"].unique())

        # build indexed dataframe
        orig_grouped = orig_data.groupby("name")

        sat_iterator = [(orig_grouped.get_group(sat).copy(), sat) for sat in sats]

        r = list(tqdm.tqdm(pool.imap_unordered(functools.partial(_propagate, start_time, end_time, output_dir), sat_iterator, chunksize=10), total=len(sats)))

        pool.close()
        pool.join()
