#!/usr/bin/env python3
#
# Usage: make_video.1.py <input_files>

import functools
import os
import sys
import glob

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import tqdm

if __name__ == "__main__":

    # parse arguments

    # if len(sys.argv) < 2:
    #     print("Usage: make_video.1.py <input_files>")
    #     sys.exit(1)

    # input_files = sys.argv[1]
    input_files = "propagated/STARLINK*.csv"

    # get all the files in the propagated directory
    files = glob.glob(input_files)

    # make a dict of the files and the sat names
    # sat_files = {int(os.path.basename(f).split(".")[0][len("ONEWEB-"):]): pd.read_csv(f) for f in files}
    sat_files = {int(os.path.basename(f).split(".")[0][len("STARLINK-"):][:4]): pd.read_csv(f) for f in tqdm.tqdm(files)}

    # now animate movement of each satellite
    fig_anim = plt.figure()
    ax_anim = fig_anim.add_subplot(projection='3d')

    cp = sns.color_palette("crest", as_cmap=True)

    time_text = ax_anim.text2D(0, .1, '', fontsize=15)

    # only use every 100th frame

    # get any satellite
    sat = list(sat_files.keys())[0]
    dates = sat_files[sat]['date']

    # start = 26000
    start = 0
    # end = len(sat_files[395])
    end = len(sat_files[sat])

    max_sat = max(sat_files.keys())

    step_size = 20

    def animate(i, max_frames):
        i *= step_size

        ax_anim.clear()
        time_text.set_text(f"t = {dates[i]}")

        for sat, df in sat_files.items():
            ax_anim.plot(df['x'][i:i+2], df['y'][i:i+2], df['z'][i:i+2], color=cp(df['distance_baseline'][i]/10000))

    frames = int((end - start) / step_size)

    anim = animation.FuncAnimation(fig_anim, functools.partial(animate, max_frames=frames), frames=frames, interval=10, blit=False)

    with tqdm.tqdm(total=frames) as pbar:
        anim.save("animation-starlink-distance.mp4",  progress_callback = lambda i, n: pbar.update(1), writer=animation.FFMpegWriter(fps=24, codec="h264_videotoolbox", bitrate=1000000))