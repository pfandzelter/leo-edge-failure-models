import os

import pandas as pd
import tqdm

import config

output_file = os.path.join(".", "results.csv")

results_folder = os.path.join(".", "distances-results")

if __name__ == "__main__":
    results = []

    to_analyze = []

    for shell in config.SHELLS:
        for i in range(int(config.STEPS / config.INTERVAL)):
            to_analyze.append((shell, i))

    for shell, i in tqdm.tqdm(to_analyze):
        p = results_folder
        p = os.path.join(p, f"{shell['name']}")
        p = os.path.join(p, f"{i}.csv")
        df = pd.read_csv(p)
        df["shell"] = shell["name"]
        df["t"] = i * config.INTERVAL
        results.append(df)

    print("Concatenating results...")
    df = pd.concat(results)
    del results

    print("Sorting results...")
    df = df.reset_index(drop=True)

    print("Saving results...")
    df.to_csv(output_file, index=False)
