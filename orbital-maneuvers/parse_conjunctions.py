#!/usr/bin/env python3
#
# Convert archived conjunction data to CSV for further analysis
#
# Usage: parse_conjunctions.py <input-file-prefix> <output-file-prefix>  <sat-prefix>
#

import sys
import glob
from datetime import datetime
import time
import os

from bs4 import BeautifulSoup
import tqdm

if __name__ == '__main__':

    # parse arguments

    if len(sys.argv) != 4:
        print('Usage: parse_conjunctions.py <input-file-prefix> <output-file-prefix> <sat-prefix>')
        sys.exit(1)

    input_file_prefix = sys.argv[1]
    output_file_prefix = sys.argv[2]
    sat_prefix = sys.argv[3]

    os.makedirs(output_file_prefix, exist_ok=True)

    out_files = {}

    # find all files with the given prefix
    for filename in tqdm.tqdm(glob.glob(input_file_prefix + "*"), desc="processing files"):

        # read all available TLE data
        conjunctions = {}

        # date is in the filename in iso format
        # format: blab-labla-2023-01-17T00:31:01.827049.html
        date = filename[-len("2023-01-17T00:31:01.827049.html"):-len(".html")]

        with open(filename, 'r') as f:
            # parse HTML data
            # t1 = time.perf_counter()
            # soup = BeautifulSoup(f, 'html.parser')
            # t2 = time.perf_counter()

            # this took too long
            # if you don't feel like installing lxml, you can use html.parser
            soup = BeautifulSoup(f, 'lxml')

            # print(f"parsing {filename} took {t2-t1} seconds")

            # find the reported date
            # sample HTML:
            # <table class=center width=650>
            # <tr align=center><td>
            # <p><i>Data current as of 2023 Jan 25 00:05 UTC</i></p>
            # <p>Computation Interval: Start = 2023 Jan 25 00:00:00.000, Stop = 2023 Feb 01 00:00:00.000<br>
            # Computation Threshold: 5.0 km<br>
            # Considering: 9,930 Primaries, 23,984 Secondaries (130,551 Conjunctions)
            # </p>
            # </td></tr>
            # </table>

            # find the table with the class "center"
            table = soup.find("table", {"class": "center", "width": 650})

            # find the first <p> in the table
            p = table.find("p")
            # find the first <i> in the <p>
            i = p.find("i")
            # the text of the <i> contains the date
            reported_date = i.text[len("Data current as of "):]
            # convert to iso format using datetime
            reported_date = datetime.strptime(reported_date, "%Y %b %d %H:%M %Z").isoformat()

            # each conjunction is a form called with target "conjunction"
            for form in soup.find_all("form", {"target": "conjunction"}):
                # there are two <tr> in each form
                # the first <tr> contains most data
                tr = form.find("tr")

                # skip the <td> with the "TLE Data" value
                td = tr.find("td")

                # the first <td> contains the first satellite number
                td = td.find_next_sibling("td")
                no1 = td.text.strip()

                # the second <td> contains the first satellite name
                td = td.find_next_sibling("td")
                name1 = td.text.strip()

                # remove the stupid [-] from the name if it exists
                if name1[-1:] == "]":
                    name1 = name1[:-4]
                    name1.strip()

                # the third <td> contains the conjunction days since epoch of the first satellite
                td = td.find_next_sibling("td")
                days_since_epoch1 = td.text.strip()

                # the fourth <td> contains the conjunction probability
                td = td.find_next_sibling("td")
                probability = td.text.strip()

                # the fifth <td> contains the conjunction dilution threshold
                td = td.find_next_sibling("td")
                dilution_threshold = td.text.strip()

                # the sixth <td> contains the conjunction min range
                td = td.find_next_sibling("td")
                min_range = td.text.strip()

                # the seventh <td> contains the conjunction relative velocity
                td = td.find_next_sibling("td")
                relative_velocity = td.text.strip()

                # the second <tr> contains the second satellite number and name
                tr = tr.find_next_sibling("tr")

                # the first <td> contains the second satellite number
                td = tr.find("td")
                no2 = td.text.strip()

                # the second <td> contains the second satellite name
                td = td.find_next_sibling("td")
                name2 = td.text.strip()

                # remove the stupid [-] from the name if it exists
                if name2[-1:] == "]":
                    name2 = name2[:-4]
                    name2.strip()

                # the third <td> contains the days since epoch of the second satellite
                td = td.find_next_sibling("td")
                days_since_epoch2 = td.text.strip()

                # the fourth <td> contains the conjunction date start
                td = td.find_next_sibling("td")
                date_start = td.text.strip()
                # change the date format from "2023 Jan 11 05:09:20.223" to iso (UTC)
                date_start = datetime.strptime(date_start, "%Y %b %d %H:%M:%S.%f").isoformat()

                # the fifth <td> contains the conjunction date TCA
                td = td.find_next_sibling("td")
                date_tca = td.text.strip()
                date_tca = datetime.strptime(date_tca, "%Y %b %d %H:%M:%S.%f").isoformat()

                # the sixth <td> contains the conjunction date end
                td = td.find_next_sibling("td")
                date_end = td.text.strip()
                date_end = datetime.strptime(date_end, "%Y %b %d %H:%M:%S.%f").isoformat()

                # save everything in a dict

                conjunction = {
                    "reported_date": reported_date,
                    "date": date,
                    "name1": name1,
                    "name2": name2,
                    "probability": probability,
                    "dilution_threshold": dilution_threshold,
                    "min_range": min_range,
                    "relative_velocity": relative_velocity,
                    "no1": no1,
                    "no2": no2,
                    "days_since_epoch1": days_since_epoch1,
                    "days_since_epoch2": days_since_epoch2,
                    "date_start": date_start,
                    "date_tca": date_tca,
                    "date_end": date_end,
                }

                conjunctions.setdefault(name1, []).append(conjunction)
                conjunctions.setdefault(name2, []).append(conjunction)

        for name, conjunctions in conjunctions.items():
            # skip some weird sats
            if not name.startswith(sat_prefix):
                continue

            if not name in out_files:
                out_files[name] = f"{output_file_prefix}{name}.csv"
                with open(out_files[name], 'w') as f:
                    # write header
                    f.write("reported_date,date,name1,name2,probability,dilution_threshold,min_range,relative_velocity,no1,no2,days_since_epoch1,days_since_epoch2,date_start,date_tca,date_end\n")

            # write conjunction data to CSV file
            with open(out_files[name], 'a') as f:
                for conjunction in conjunctions:
                    # write conjunction data
                    f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        conjunction["reported_date"],
                        conjunction["date"],
                        conjunction["name1"],
                        conjunction["name2"],
                        conjunction["probability"],
                        conjunction["dilution_threshold"],
                        conjunction["min_range"],
                        conjunction["relative_velocity"],
                        conjunction["no1"],
                        conjunction["no2"],
                        conjunction["days_since_epoch1"],
                        conjunction["days_since_epoch2"],
                        conjunction["date_start"],
                        conjunction["date_tca"],
                        conjunction["date_end"],
                    ))
