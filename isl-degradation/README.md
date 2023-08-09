# ISL Degradation

This directory contains tools to calculate the distance of ISLs for different LEO satellite megaconstellations.

Requirements are Python (probably version 3.9) and Jupyter.

1. Install at least the dependencies in `requirements.txt`:

    ```sh
    python3 -m pip install -r requirements.txt
    ```

1. Configure the parameters in `config.py`.

1. Run `distances.py` to calculate ISL distances:

    ```sh
    python3 distances.py
    ```

    This will create and fill a folder called `distances-results`.

1. Run `combine.py` to combine results into a results file (called `results.csv`):

    ```sh
    python3 combine.py
    ```

1. Analyze these results with the `analyze.ipynb` notebook.
