#
# Copyright (c) Tobias Pfandzelter. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for details.
#

import os
import numpy as np
import scipy.constants
import scipy.special

# whether to show animations of simulated constellations
ANIMATE = False

# whether to print debug information
DEBUG = False

# number of columns in the output terminal
TERM_SIZE = 80

# radius of earth in km
# EARTH_RADIUS = 6371.0
EARTH_RADIUS_POLAR = 6356.7523
EARTH_RADIUS_EQUATORIAL = 6378.1370

# minimum altitude for communications
# altitude of Thermosphere in km
MIN_COMMS_ALTITUDE = 80

# model to use for satellite orbits
# can be SGP4 or Kepler
MODEL = "SGP4"

# simulation interval in seconds
INTERVAL = 1

# total length of the simulation in seconds
STEPS = 6000

# speed of light in km/s
C = scipy.constants.speed_of_light / 1000.0

# output folders
__root = os.path.abspath(os.path.dirname(__file__)) if __file__ else "."
DISTANCES_DIR = os.path.join(__root, "distances-results")
os.makedirs(DISTANCES_DIR, exist_ok=True)

# constellation shells to consider
SHELLS = [
    # put these down as configurations
    # Starlink 1: 72,22, 53.0, 550
    {
        "name": "st1",
        "planes": 72,
        "sats": 22,
        "altitude": 550,
        "inc": 53.0,
    },
    # Starlink 2: 72, 22, 53.2, 540
    {
        "name": "st2",
        "planes": 72,
        "sats": 22,
        "altitude": 540,
        "inc": 53.2,
    },
    # Starlink 3: 36, 20, 70.0, 570
    {
        "name": "st3",
        "planes": 36,
        "sats": 20,
        "altitude": 570,
        "inc": 70.0,
    },
    # Starlink 4: 6, 58, 97.6, 560
    {
        "name": "st4",
        "planes": 6,
        "sats": 58,
        "altitude": 560,
        "inc": 97.6,
    },
    # Starlink 5: 4, 43, 97.6, 560
    {
        "name": "st5",
        "planes": 4,
        "sats": 43,
        "altitude": 560,
        "inc": 97.6,
    },
    # Kuiper 1: 34, 34, 51.9, 630
    {
        "name": "ku1",
        "planes": 34,
        "sats": 34,
        "altitude": 630,
        "inc": 51.9,
    },
    # Kuiper 2: 28, 28, 33.0, 590

    {
        "name": "ku2",
        "planes": 28,
        "sats": 28,
        "altitude": 590,
        "inc": 33.0,
    },
    # Kuiper 3: 36, 36, 42.0, 610
    {
        "name": "ku3",
        "planes": 36,
        "sats": 36,
        "altitude": 610,
        "inc": 42.0,
    },
    # OneWeb 1: 36, 49, 87.9, 1200
    {
        "name": "ow1",
        "planes": 36,
        "sats": 49,
        "altitude": 1200,
        "inc": 87.9,
    },
    # OneWeb 2: 32, 72, 40.0, 1200
    {
        "name": "ow2",
        "planes": 32,
        "sats": 72,
        "altitude": 1200,
        "inc": 40.0,
    },
    # OneWeb 3: 32, 72, 55.0, 1200
    {
        "name": "ow3",
        "planes": 32,
        "sats": 72,
        "altitude": 1200,
        "inc": 55.0,
    },
]
