#
# Copyright (c) Tobias Pfandzelter. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for details.
#

import tqdm
import os
import sys
import concurrent.futures

import config
from simulation.simulation import Simulation

sys.path.append(os.path.abspath(os.getcwd()))

def run_simulation(steps: int, interval: float, planes: int, nodes: int, inc: float, altitude: int, name: str, animate: bool, write: bool, results_folder: str):

    results_dir = os.path.join(results_folder, name)
    os.makedirs(results_dir, exist_ok=True)

    # setup simulation
    s = Simulation(planes=planes, nodes_per_plane=nodes, inclination=inc, semi_major_axis=int(altitude + config.EARTH_RADIUS_EQUATORIAL)*1000, earth_radius_equatorial=int(config.EARTH_RADIUS_EQUATORIAL * 1000), earth_radius_polar=int(config.EARTH_RADIUS_POLAR * 1000), min_communications_altitude=int(config.MIN_COMMS_ALTITUDE * 1000), model=config.MODEL, animate=animate, report_status=config.DEBUG)
    # for each timestep, run simulation

    total_steps = int(steps/interval)
    for step in tqdm.trange(total_steps, desc="simulating {}".format(name)):
    # for step in range(total_steps):
        next_time = step*interval

        fname = os.path.join(results_dir, "{}.csv".format(next_time) if write else os.devnull)

        with open(fname, "w") as f:
            f.write("a,b,distance,height,active\n")
            s.update_model(next_time, result_file=f)

    if s.animation is not None:
        s.animation.terminate()

    s.terminate()

if __name__ == "__main__":

    shells = [s["name"] for s in config.SHELLS]
    parallel = True
    animate = config.ANIMATE
    write = True

    if len(sys.argv) > 1:
        shells = set(sys.argv[1:])
        parallel = False
        animate = True
        write = False

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for s in config.SHELLS:
            if not s["name"] in shells:
                continue

            PLANES = s["planes"]
            # Number of nodes/plane
            NODES = s["sats"]

            # Plane inclination (deg)
            INC = s["inc"]

            # Orbit Altitude (Km)
            ALTITUDE = s["altitude"]

            NAME = s["name"]

            if parallel:
                executor.submit(run_simulation, config.STEPS, config.INTERVAL, int(PLANES), int(NODES), float(INC), int(ALTITUDE), NAME, animate, write, config.DISTANCES_DIR)
            else:
                run_simulation(config.STEPS, config.INTERVAL, int(PLANES), int(NODES), float(INC), int(ALTITUDE), NAME, animate, write, config.DISTANCES_DIR)
