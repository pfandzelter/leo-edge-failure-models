#
# This file is part of leo-edge-failure-models
# (https://github.com/pfandzelter/leo-edge-failure-models).
# Copyright (c) 2023 Ben S. Kempton, Tobias Pfandzelter.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# gotta have numpy
import numpy as np
import numpy.typing as npt

# used to calculate kepler 2 body orbits
from PyAstronomy import pyasl
import sgp4.api as sgp4

import math

import tqdm
import typing

# try to import numba funcs
try:
    import numba

    USING_NUMBA = True
except ModuleNotFoundError:
    USING_NUMBA = False
    print("you probably do not have numba installed...")
    print("reverting to non-numba mode")

# earth"s z axis (eg a vector in the positive z direction)
EARTH_ROTATION_AXIS = [0, 0, 1]

# number of seconds per earth rotation (day)
SECONDS_PER_DAY = 86400

# according to wikipedia
STD_GRAVITATIONAL_PARAMATER_EARTH = 3.986004418e14

# how big to initialize the ground point array...
NUM_GROUND_POINTS = 0

# The numpy data type used to store satellite data
# note  use of int16 for names: max number of satellites = (2^15)-1
# note use of int32 for position: max pos value = (2^31)-1 meters
#    (this is 5.5 times the distance to the moon
#     and should be fine for earth orbit simulation)
# Note that fields can be accessed by their name: array[idx]["ID"]
SATELLITE_DTYPE = np.dtype(
    [
        ("ID", np.int16),  # ID number, unique, = array index
        ("plane_number", np.int16),  # which orbital plane is the satellite in?
        ("offset_number", np.int16),  # What satellite withen the plane?
        ("time_offset", np.float32),  # time offset for kepler ellipse solver
        ("x", np.int32),  # x position in meters
        ("y", np.int32),  # y position in meters
        ("z", np.int32),
    ]
)  # z position in meters


# The numpy data type used to store link data
# link array size may have to be adjusted
# each index is 8 bytes
LINK_DTYPE = np.dtype(
    [
        ("node_1", np.int16),  # an endpoint of the link
        ("node_2", np.int16),  # the other endpoint of the link
        ("distance", np.int32),  # distance of the link in meters
        ("height", np.int32),  # height of the link in meters
        ("active", bool),
    ]
)  # can this link be active?

LINK_ARRAY_SIZE = 10000000  # 10 million indices = 80 megabyte array (huge)

###############################################################################
# const class


class Constellation:
    """
    A class used to contain and manage a satellite constellation

    ...

    Attributes
    ----------
    number_of_planes : int
        the number of planes in the constellation
    nodes_per_plane : int
        the number of satellites per plane
    total_sats : int
        the total number of nodes(satellites) in constellation
    ground_node_counter : int
        always negative, countdown, used to keep track of ground node IDs
    inclination : float
        the inclination of all planes in constellation
    semi_major_axis : float
        semi major axis of the orbits (radius, if orbits circular)
    period : int
        the period of the orbits in seconds
    eccentricity : float
        the eccentricity of the orbits; range = 0.0 - 1.0
    satellites_array : SATELLITE_DTYPE
        numpy array of satellite_dtype, contains satellite data
    raan_offsets : List[float]
        list of floats, keeps track of all the ascending node offsets in degrees
    plane_solvers : List[ke_solver]
        contains the PyAstronomy Kepler Ellipse solver for each orbital plane
    time_offsets : List[float]
        contains the time offsets for satellties withen a plane
    current_time : int
        keeps track of the current simulation time

    Methods
    -------
    initSatelliteArray(sat_array=None)
        fills the sat array with initial values for time=0
    getArrayOfNodePositions()
        returns a a slice of the constellation array, containing only position values
    setconstellationTime(time=0.0)
        updates all satellites and ground stations positions to reflect the new time
    """

    def __init__(
        self,
        planes: int = 1,
        nodes_per_plane: int = 4,
        inclination: float = 0,
        semi_major_axis: int = 6372000,
        ecc: float = 0.0,
        min_communications_altitude: int = 100000,
        use_SGP4: bool = False,
        earth_radius_equatorial: int = 6371000,
        earth_radius_polar: int = 6371000,
        arc_of_ascending_nodes: float = 360.0,
    ):
        """
        Parameters
        ----------
        planes : int
            the number of planes in the constellation
        nodes_per_plane : int
            the number of satellites per plane
        inclination : float
            the inclination of all planes in constellation
        semi_major_axis : float
            semi major axis of the orbits (radius, if orbits circular)
        ecc : float
            the eccentricity of the orbits; range = 0.0 - 1.0
        minCommunicationsAltitude : int32
            The minimum altitude that inter satellite links must pass
            above the Earth"s surface.
        minSatElevation : int
            The minimum angle of elevation in degrees above the horizon a satellite
            needs to have for a ground station to communicate with it.
        linkingMethod : string
            The current linking method used by the constellation
            currently only used for generating GML files.
        arcOfAscendingNodes : float
            The angle of arc (in degrees) that the ascending nodes of all the
            orbital planes is evenly spaced along. Ex, seting this to 180 results
            in a Pi constellation like Iridium
        """

        self.number_of_planes = planes
        self.nodes_per_plane = nodes_per_plane
        self.total_sats = planes * nodes_per_plane
        self.ground_node_counter = 0
        self.inclination = inclination
        self.semi_major_axis = semi_major_axis
        self.period = self.calculate_orbit_period(semi_major_axis=self.semi_major_axis)
        self.eccentricity = ecc
        self.earth_radius_equatorial = earth_radius_equatorial
        self.earth_radius_polar = earth_radius_polar
        self.current_time = 0
        self.number_of_isl_links = 0
        self.number_of_gnd_links = 0
        self.total_links = 0
        self.link_array_size = LINK_ARRAY_SIZE
        self.min_communications_altitude = min_communications_altitude
        self.min_sat_elevation = 40
        self.use_SGP4 = use_SGP4
        self.G = None

        # this is not written to zero, because it has it"s own init
        # function a a few lines down: initSatelliteArray()
        self.satellites_array = np.empty(self.total_sats, dtype=SATELLITE_DTYPE)

        # declare an empty link array
        self.link_array = np.zeros(self.link_array_size, dtype=LINK_DTYPE)

        # figure out the time offsets for nodes withen a plane
        self.time_offsets = [
            (self.period / nodes_per_plane) * i for i in range(0, nodes_per_plane)
        ]

        # initialize the satellite array
        if self.use_SGP4:

            if not sgp4.accelerated:
                print(
                    "\033[93m⚠️  SGP4 C++ API not available on your system, falling back to slower Python implementation...\033[0m"
                )

            self.init_satellite_array_sgp4(
                arc_of_ascending_nodes=arc_of_ascending_nodes
            )
        else:
            self.init_satellite_array(arc_of_ascending_nodes)

    def init_satellite_array(self, arc_of_ascending_nodes) -> None:
        """initializes the satellite array with positions at time zero

        Parameters
        ----------
        sat_array :
            the satellite array object, modified in place

        """
        # figure out how many degrees to space right ascending nodes of the planes
        raan_offsets = [
            (arc_of_ascending_nodes / self.number_of_planes) * i
            for i in range(0, self.number_of_planes)
        ]

        # generate a list with a kepler ellipse solver object for each plane
        self.plane_solvers = []
        for raan in raan_offsets:
            self.plane_solvers.append(
                pyasl.KeplerEllipse(
                    per=self.period,  # how long the orbit takes in seconds
                    a=self.semi_major_axis,  # if circular orbit, this is same as radius
                    e=self.eccentricity,  # generally close to 0 for leo constellations
                    Omega=raan,  # right ascention of the ascending node
                    w=0.0,  # initial time offset / mean anamoly
                    i=self.inclination,
                )
            )  # orbit inclination
        # we offset each plane by a small amount, so they do not "collide"
        # this little algorithm comes up with a list of offset values
        # phase_offset = ((self.period / self.nodes_per_plane) /
        #                           2.0)
        # temp = []
        # toggle = False
        # # this loop results puts thing in an array in this order:
        # # [...8,6,4,2,0,1,3,5,7...]
        # # so that the offsets in adjacent planes are similar
        # # basically do not want the max and min offset in two adjcent planes
        # for i in range(self.number_of_planes):
        #     if toggle:
        #         temp.append(phase_offset)
        #     else:
        #         temp.append(0.0)
        #         # temp.append(phase_offset)
        #     toggle = not toggle

        # phase_offsets = temp

        # loop through all satellites
        for plane in range(0, self.number_of_planes):
            for node in range(0, self.nodes_per_plane):

                # calculate the KE solver time offset
                # offset = (self.time_offsets[node] + phase_offsets[plane])
                offset = self.time_offsets[node]
                # calculate the unique ID of the node (same as array index)
                unique_id = (plane * self.nodes_per_plane) + node

                # calculate initial position
                init_pos = self.plane_solvers[plane].xyzPos(offset)

                # update satellties array
                self.satellites_array[unique_id]["ID"] = np.int16(unique_id)
                self.satellites_array[unique_id]["plane_number"] = np.int16(plane)
                self.satellites_array[unique_id]["offset_number"] = np.int16(node)
                self.satellites_array[unique_id]["time_offset"] = np.float32(offset)
                self.satellites_array[unique_id]["x"] = np.int32(init_pos[0])
                self.satellites_array[unique_id]["y"] = np.int32(init_pos[1])
                self.satellites_array[unique_id]["z"] = np.int32(init_pos[2])

    def init_satellite_array_sgp4(self, arc_of_ascending_nodes) -> None:
        """initializes the satellite array with positions at time zero

        Parameters
        ----------
        sat_array :
            the satellite array object, modified in place

        """

        MODEL = sgp4.WGS84
        MODE = "i"
        BSTAR = 0.0
        NDOT = 0.0
        ARGPO = 0.0
        START_JD, START_FR = 0.0, 0.0

        # we offset each plane by a small amount, so they do not "collide"
        # this little algorithm comes up with a list of offset values
        # phase_offset = ((self.period / self.nodes_per_plane) /
        #                           2.0)
        # temp = []
        # toggle = False
        # # this loop results puts thing in an array in this order:
        # # [...8,6,4,2,0,1,3,5,7...]
        # # so that the offsets in adjacent planes are similar
        # # basically do not want the max and min offset in two adjcent planes
        # for i in range(self.number_of_planes):
        #     if toggle:
        #         temp.append(phase_offset)
        #     else:
        #         temp.append(0.0)
        #         # temp.append(phase_offset)
        #     toggle = not toggle

        # phase_offsets = temp

        raan_offsets = [
            (arc_of_ascending_nodes / self.number_of_planes) * i
            for i in range(0, self.number_of_planes)
        ]

        self.period = int(
            2.0
            * math.pi
            * math.sqrt(
                math.pow(self.semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMATER_EARTH
            )
        )

        self.time_offsets = [
            (self.period / self.nodes_per_plane) * i
            for i in range(0, self.nodes_per_plane)
        ]

        self.sgp4_solvers = [sgp4.Satrec()] * self.total_sats

        for plane in range(0, self.number_of_planes):
            for node in range(0, self.nodes_per_plane):

                unique_id = (plane * self.nodes_per_plane) + node

                self.sgp4_solvers[unique_id] = sgp4.Satrec()

                self.sgp4_solvers[unique_id].sgp4init(
                    # whichconst=
                    MODEL,  # gravity model
                    # opsmode=
                    MODE,  # 'a' = old AFSPC mode, 'i' = improved mode
                    # satnum=
                    unique_id,  # satnum: Satellite number
                    # epoch=
                    START_JD,  # epoch: days since 1949 December 31 00:00 UT
                    # bstar=
                    BSTAR,  # bstar: drag coefficient (/earth radii)
                    # ndot=
                    NDOT,  # ndot: ballistic coefficient (revs/day)
                    # nddot=
                    0.0,  # nddot: second derivative of mean motion (revs/day^3)
                    # ecco=
                    self.eccentricity,  # ecco: eccentricity
                    # argpo=
                    np.radians(
                        ARGPO
                    ),  # argpo: argument of perigee (radians) -> zero for circular orbits
                    # inclo=
                    np.radians(self.inclination),  # inclo: inclination (radians)
                    # mo=
                    # np.radians((node + (phase_offsets[plane]*self.nodes_per_plane / self.period)) * (360.0 / self.nodes_per_plane) + self.time_offsets[node]/self.period), # mo: mean anomaly (radians) -> starts at 0 plus offset for the satellites
                    np.radians(
                        (node) * (360.0 / self.nodes_per_plane)
                        + self.time_offsets[node] / self.period
                    ),  # mo: mean anomaly (radians) -> starts at 0 plus offset for the satellites
                    # no_kozai=
                    np.radians(360.0)
                    / (self.period / 60),  # no_kozai: mean motion (radians/minute)
                    # nodeo=
                    np.radians(
                        raan_offsets[plane]
                    ),  # nodeo: right ascension of ascending node (radians)
                )

                # calculate initial position
                e, r, d = self.sgp4_solvers[unique_id].sgp4(START_JD, START_FR)

                # init satellties array
                self.satellites_array[unique_id]["ID"] = np.int16(unique_id)
                self.satellites_array[unique_id]["plane_number"] = np.int16(plane)
                self.satellites_array[unique_id]["offset_number"] = np.int16(node)
                self.satellites_array[unique_id]["x"] = np.int32(r[0]) * 1000
                self.satellites_array[unique_id]["y"] = np.int32(r[1]) * 1000
                self.satellites_array[unique_id]["z"] = np.int32(r[2]) * 1000

    def get_array_of_node_positions(self) -> npt.NDArray[typing.Any]:
        """copies a sub array of only position data from
        satellite AND groundpoint arrays

        Returns
        -------
        positions : np array
            a copied sub array of the satellite array, that only contains positions data
        """

        return np.copy(self.satellites_array[["x", "y", "z"]])

    def get_array_of_sat_positions(self) -> npt.NDArray[typing.Any]:
        """copies a sub array of only position data from
        satellite array

        Returns
        -------
        sat_positions : np array
            a copied sub array of the satellite array, that only contains positions data
        """

        return np.copy(self.satellites_array[["x", "y", "z"]])

    def get_array_of_links(self) -> npt.NDArray[typing.Any]:
        """copies a sub array of link data

        Returns
        -------
        links : np array
            contains all links
        """
        total_links = self.total_links
        links = np.copy(self.link_array[:total_links])

        return links

    def set_constellation_time(self, time: float = 0.0) -> None:
        """updates all position and link data to specified time

        Parameters
        ----------
        time : float
            simulation time to set to in seconds

        Returns
        -------
        None
        """

        # cast time to an int
        self.current_time = int(time)

        if self.use_SGP4:
            self.update_sat_pos_sgp4()
        else:
            self.update_sat_pos()

        return None

    def update_sat_pos(self) -> None:
        for sat_id in range(self.satellites_array.size):
            pos = self.plane_solvers[
                self.satellites_array[sat_id]["plane_number"]
            ].xyzPos(self.current_time + self.satellites_array[sat_id]["time_offset"])

            self.satellites_array[sat_id]["x"] = np.int32(pos[0])
            self.satellites_array[sat_id]["y"] = np.int32(pos[1])
            self.satellites_array[sat_id]["z"] = np.int32(pos[2])

    def update_sat_pos_sgp4(self) -> None:
        fr = 0.0 + (self.current_time / SECONDS_PER_DAY)

        for sat_id in range(self.satellites_array.size):
            e, r, d = self.sgp4_solvers[sat_id].sgp4(0.0, fr)

            self.satellites_array[sat_id]["x"] = np.int32(r[0]) * 1000
            self.satellites_array[sat_id]["y"] = np.int32(r[1]) * 1000
            self.satellites_array[sat_id]["z"] = np.int32(r[2]) * 1000

    def calculate_orbit_period(self, semi_major_axis: float = 0.0) -> int:
        """calculates the period of a orbit for Earth

        Parameters
        ----------
        semi_major_axis : float
            semi major axis of the orbit in meters

        Returns
        -------
        Period : int
            the period of the orbit in seconds (rounded to whole seconds)
        """

        tmp = math.pow(semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMATER_EARTH
        return int(2.0 * math.pi * math.sqrt(tmp))

    def get_rotation_matrix(self, axis: np.ndarray, degrees: float) -> np.ndarray:
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.

        Parameters
        ----------
        axis : list[x, y, z]
            a vector defining the rotaion axis
        degrees : float
            The number of degrees to rotate

        """

        theta = math.radians(degrees)
        axis = np.asarray(axis)
        axis = axis / math.sqrt(np.dot(axis, axis))
        a = math.cos(theta / 2.0)
        b, c, d = -axis * math.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array(
            [
                [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
            ]
        )

    def init_plus_grid_links(self, crosslink_interpolation: int = 1) -> None:
        self.number_of_isl_links = 0

        temp = self.numba_init_plus_grid_links(
            self.link_array,
            self.link_array_size,
            self.number_of_planes,
            self.nodes_per_plane,
            crosslink_interpolation=crosslink_interpolation,
        )
        if temp is not None:
            self.number_of_isl_links = temp[0]
            self.total_links = self.number_of_isl_links

    @staticmethod
    @numba.njit  # type: ignore
    def numba_init_plus_grid_links(
        link_array: np.ndarray,
        link_array_size: int,
        number_of_planes: int,
        nodes_per_plane: int,
        crosslink_interpolation: int = 1,
    ) -> typing.Tuple[int]:

        link_idx = 0

        # add the intra-plane links
        for plane in range(number_of_planes):
            for node in range(nodes_per_plane):
                node_1 = node + (plane * nodes_per_plane)
                if node == nodes_per_plane - 1:
                    node_2 = plane * nodes_per_plane
                else:
                    node_2 = node + (plane * nodes_per_plane) + 1

                if link_idx < link_array_size - 1:
                    link_array[link_idx]["node_1"] = np.int16(node_1)
                    link_array[link_idx]["node_2"] = np.int16(node_2)
                    link_idx = link_idx + 1
                else:
                    print(
                        "❌ ERROR! ran out of room in the link array for intra-plane links"
                    )
                    return (0,)

        # add the cross-plane links
        for plane in range(number_of_planes):
            if plane == number_of_planes - 1:
                plane2 = 0
            else:
                plane2 = plane + 1
            for node in range(nodes_per_plane):
                node_1 = node + (plane * nodes_per_plane)
                node_2 = node + (plane2 * nodes_per_plane)
                if link_idx < link_array_size - 1:
                    if (node_1 + 1) % crosslink_interpolation == 0:
                        link_array[link_idx]["node_1"] = np.int16(node_1)
                        link_array[link_idx]["node_2"] = np.int16(node_2)
                        link_idx = link_idx + 1
                else:
                    print(
                        "❌ ERROR! ran out of room in the link array for cross-plane links"
                    )
                    return (0,)

        number_of_isl_links = link_idx

        return (number_of_isl_links,)

    def update_plus_grid_links(
        self,
        earth_radius_equatorial: float,
        earth_radius_polar: float,
        min_communications_altitude: float,
    ) -> None:
        """
        connect satellites in a +grid network

        Parameters
        ----------
        initialize : bool
            Because PlusGrid ISL are static, they only need to be generated once,
            If initialize=False, only update link distances, do not regererate
        crosslink_interpolation : int
            This value is used to make only 1 out of every crosslink_interpolation
            satellites able to have crosslinks. For example, with a interpolation
            value of '2', only every other satellite will have crosslinks, the rest
            will have only intra-plane links

        """

        temp = self.numba_update_plus_grid_links(
            total_sats=self.total_sats,
            satellites_array=self.satellites_array,
            link_array=self.link_array,
            link_array_size=self.link_array_size,
            number_of_isl_links=self.number_of_isl_links,
            earth_radius_equatorial=earth_radius_equatorial,
            earth_radius_polar=earth_radius_polar,
            min_communications_altitude=min_communications_altitude,
        )

        # # if yes, we have an issue!
        # for link in self.link_array[:self.number_of_isl_links]:
        #     if not link['active']:
        #         # find the height of the link above the ellipsis spanned by the two radii
        #         print(f'❌ ERROR! link between {link["node_1"]} and {link["node_2"]} is not active with height {link["height"]} (< {max(earth_radius_equatorial, earth_radius_polar) + min_communications_altitude})!')

    @staticmethod
    @numba.njit  # type: ignore
    def numba_update_plus_grid_links(
        total_sats: int,
        satellites_array: np.ndarray,
        link_array: np.ndarray,
        link_array_size: int,
        number_of_isl_links: int,
        earth_radius_equatorial: float,
        earth_radius_polar: float,
        min_communications_altitude: float,
    ) -> None:

        for isl_idx in range(number_of_isl_links):
            sat_1 = link_array[isl_idx]["node_1"]
            sat_2 = link_array[isl_idx]["node_2"]
            d = int(
                math.sqrt(
                    math.pow(
                        satellites_array[sat_1]["x"] - satellites_array[sat_2]["x"], 2
                    )
                    + math.pow(
                        satellites_array[sat_1]["y"] - satellites_array[sat_2]["y"], 2
                    )
                    + math.pow(
                        satellites_array[sat_1]["z"] - satellites_array[sat_2]["z"], 2
                    )
                )
            )

            link_array[isl_idx]["distance"] = d

            # caclulate the height of the triangle spanned by the two satellites and the earth
            # check if this height is smaller than max(earth_radius_equatorial, earth_radius_polar) + min_comms_altitude

            # a is distance between sat1 and 0,0,0
            a = math.sqrt(
                math.pow(satellites_array[sat_1]["x"], 2)
                + math.pow(satellites_array[sat_1]["y"], 2)
                + math.pow(satellites_array[sat_1]["z"], 2)
            )

            # b is distance between sat2 and 0,0,0
            b = math.sqrt(
                math.pow(satellites_array[sat_2]["x"], 2)
                + math.pow(satellites_array[sat_2]["y"], 2)
                + math.pow(satellites_array[sat_2]["z"], 2)
            )

            # c is distance between sat1 and sat2
            # that's also d
            c = math.sqrt(
                math.pow(satellites_array[sat_1]["x"] - satellites_array[sat_2]["x"], 2)
                + math.pow(
                    satellites_array[sat_1]["y"] - satellites_array[sat_2]["y"], 2
                )
                + math.pow(
                    satellites_array[sat_1]["z"] - satellites_array[sat_2]["z"], 2
                )
            )

            # now derive the area of the triangle using herons formula
            s = (a + b + c) / 2
            A = math.sqrt(s * (s - a) * (s - b) * (s - c))

            # now derive the height of the triangle
            h = 2 * A / c

            link_array[isl_idx]["height"] = h

            # now check if the height is smaller than the max earth radius + min comms altitude

            link_array[isl_idx]["active"] = (
                h
                >= max(earth_radius_equatorial, earth_radius_polar)
                + min_communications_altitude
            )

            # # if yes, we have an issue!
            # if not link_array[isl_idx]['active']:
            #     # find the height of the link above the ellipsis spanned by the two radii
            #     print('ERROR! link between sat ' + str(sat_1) + ' and sat ' + str(sat_2) + ' is too high!')
            #     print('    height above ellipsis: ' + str(h))
