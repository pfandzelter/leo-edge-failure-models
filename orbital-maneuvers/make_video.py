#!/usr/bin/env python3
#
# Usage: graph_sat.py <input_file>

import functools
import os
import sys

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import tqdm

if __name__ == "__main__":

    # parse arguments

    if len(sys.argv) < 2:
        print("Usage: graph_sat.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    sat_name = os.path.basename(input_file).split(".")[0]

    output_file = f"anim-{sat_name}.mp4"

    # df = pd.read_csv("propagated/ONEWEB-0395.csv")
    df = pd.read_csv(input_file)

    fig_anim = plt.figure()

    ax_anim = fig_anim.add_subplot(111, projection='3d')

    cp = sns.color_palette("crest", as_cmap=True)

    time_text = ax_anim.text2D(0, .1, '', fontsize=15)

    start = 26000
    end = len(df)

    def animate(i, max_frames):
        # ax_anim.clear()

        index = i + start

        time_text.set_text(f"t = {df['date'][index]}")

        ax_anim.scatter(df['x'][index], df['y'][index], df['z'][index], marker="x", color=cp(i/max_frames))

        return ax_anim,

    frames = end - start

    anim = animation.FuncAnimation(fig_anim, functools.partial(animate, max_frames=frames), frames=frames, blit=False)

    with tqdm.tqdm(total=frames) as pbar:
        anim.save(output_file, progress_callback = lambda i, n: pbar.update(1), writer=animation.FFMpegWriter(fps=60, codec="h264_videotoolbox"))
