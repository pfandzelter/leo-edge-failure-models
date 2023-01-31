#!/usr/bin/env python3
#
# Convert archived TLE data to CSV for further analysis
#
# Usage: tle-to-csv.py <input-file-prefix> <output-file>
#

import sys
import glob

if __name__ == '__main__':

    # parse arguments

    if len(sys.argv) != 3:
        print('Usage: tle-to-csv.py <input-file-prefix> <output-file>')
        sys.exit(1)

    input_file_prefix = sys.argv[1]
    output_file = sys.argv[2]

    # read all available TLE data
    tle_lines = []

    # find all files with the given prefix
    for filename in glob.glob(input_file_prefix + "*"):

        # date is in the filename in iso format
        date = filename.split("-", 1)[1]
        date = date[:-len(".txt")]

        with open(filename, 'r') as f:
            # parse TLE data from file
            # read three lines at a time
            # skip lines until we find the first line with the satellite number 1
            while True:
                line1 = f.readline()
                if not line1:
                    break
                line2 = f.readline()
                line3 = f.readline()

                tle_lines.append({
                    "date": date,
                    "line1": line1,
                    "line2": line2,
                    "line3": line3,
                })

    # write TLE data to CSV file
    with open(output_file, 'w') as f:
        # write header
        f.write("date,name,line1,line2\n")

        for tle_line in tle_lines:
            # parse TLE data and write

            # sample TLE line
            # STARLINK-1007
            # 1 44713U 19074A   22352.40024299  .00000410  00000+0  46397-4 0  9991
            # 2 44713  53.0552  71.6920 0001616  51.2074 308.9059 15.06400439171475

            f.write("{date},{name},{line1},{line2}\n".format(
                date = tle_line["date"],
                name = tle_line["line1"].strip(),
                line1 = tle_line["line2"].strip(),
                line2 = tle_line["line3"].strip(),
            ))
