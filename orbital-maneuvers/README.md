# Orbital Maneuvers

Our goal was to compare publicly available two-line element (TLE) sets for satellites in LEO megaconstellations with conjunction warnings.
Our intuition was that if a conjunction happens, an anomaly should be visible in the TLE data, i.e., the satellite will move in a weird way.
We thus scraped TLE data from [CelesTrak](https://celestrak.org/) in two-hour intervals and conjunction assessment data from [CelesTrak SOCRATES](https://celestrak.org/SOCRATES/) in eight-hour intervals for two weeks in January 2023.
We limited ourselves to data on Starlink, Iridium, and OneWeb satellites.

## Scraping and Parsing Data

Our scripts to scrape TLE and conjunction assessment data are not included here.
Further, the cleaned data we have is unfortunately too large to share on GitHub and will be made available upon request.

## Propagating Data

From the TLE files, we can create a list of satellite positions over time using the `propagate_sat.py` script:

```sh
./propagate_sat.py ./cleaned/starlink.csv ./propagated
```

This will create a positional data for each unique satellite in the `propagated` directory.

## Plot Conjunctions

```sh
./plot_conjunctions.py ./cleaned/starlink-conjunctions/ ./propagated/STARLINK ./images/conjunctions
```

## Plot Orbits

```sh
./graph_sat.py ./propagated/STARLINK ./images/orbits
```
