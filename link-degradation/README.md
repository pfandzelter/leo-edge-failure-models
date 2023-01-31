# Link Degradation

Our goal here is to correlate Starlink network performance reported by [Michel et al.](https://dl.acm.org/doi/pdf/10.1145/3517745.3561416) with historical weather data from Louvain-la-Neuve, Belgium, their dish location.
Unfortunately, for the period of their experiments (roughly Winter and Spring 2022), no heavy rain was reported.
Our results are thus that light rain and cloud cover does not impact Starlink performance.

1. Download network performance data

    Download the UC Louvain data from [here](https://smartdata.polito.it/a-first-look-at-starlink-performance-open-data/).
    Download at least the `ping` and `speed-test` folders.
    Place it in a folder called `uclouvain-data`.

    If you use this data in your own work, make sure to also cite their [paper](https://dl.acm.org/doi/pdf/10.1145/3517745.3561416)!

1. Download weather data

    We have downloaded weather data for Louvain-la-Neuve from December 15, 2021 to May 15, 2022, from [Open-Meteo](https://open-meteo.com/).
    Select at least the `Temperature`, `Precipitation`, `Rain`, `Weathercode`, and `Cloudcover Total` options.

1. Place the weather data as `weather.csv` in this folder, remove the first three lines of the CSV file, and rename the columns according to our own `weather.csv`.

1. Run the `network.ipynb` notebook to parse the networking data into CSV files.

1. Run the `analyze.ipynb` notebook to analyze the data.
