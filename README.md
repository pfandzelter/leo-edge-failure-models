# Edge Computing in Low-Earth Orbit -- What Could Possibly Go Wrong?

This repository contains experiments and simulations accompanying our paper on failure scenarios for LEO edge computing.

If you use this software in a publication, please cite it as:

### Text

T. Pfandzelter and D. Bermbach, **Edge Computing in Low-Earth Orbit -- What Could Possibly Go Wrong?**, 1st ACM Workshop on LEO Networking and Communication (LEO-NET '23), Madrid, Spain. Association for Computing Machinery, New York, NY, USA. October, 2023.

### BibTeX

```bibtex
@inproceedings{pfandzelter2023failure,
    author = "Pfandzelter, Tobias and Bermbach, David",
    title = "Edge Computing in Low-Earth Orbit -- What Could Possibly Go Wrong?",
    booktitle = "Proceedings of the the 1st ACM Workshop on LEO Networking and Communication 2023",
    month = oct,
    year = 2023,
    publisher = "ACM",
    address = "New York, NY, USA",
    series = "LEO-NET '23",
    location = "Madrid, Spain",
    numpages = 6,
    doi = "10.1145/3614204.3616106",
    url = "https://doi.org/10.1145/3614204.3616106"
}
```

A preprint is available on [arXiv](https://arxiv.org/abs/2302.08952).
For a full list of publications, please see [our website](https://www.tu.berlin/en/mcc/research/publications).

### License

The code in this repository is licensed under the terms of the [MIT](./LICENSE) license.
The only exception is the simulation code in [`isl-degradation/simulation`](./isl-degradation/simulation/) adapted from [Ben-Kempton/SILLEO-SCNS](https://github.com/Ben-Kempton/SILLEO-SCNS) and licensed under the terms of the [GPLv3](./isl-degradation/simulation/LICENSE) license.

## Content

This repository contains a variety of independent tools and scripts.
They are roughly ordered in this manner:

1. [Up-/Downlink Degradation](./link-degradation/README.md)

    Artifacts used to correlate the Starlink network performance reported by [Michel et al.](https://dl.acm.org/doi/abs/10.1145/3517745.3561416) to local weather data.

1. [On-Board Compute Failure](./compute-failure/README.md)

    Data and tools to calculate the impact of radiation in LEO on compute hardware on-board satellites.

1. [Orbital Maneuvers](./orbital-maneuvers/README.md)

    Tools to scrape and analyze public data on satellite maneuvers to calculate the impact of LEO satellite orbital maneuvers on the network.

1. [Inter-Satellite Link Degradation](./isl-degradation/README.md)

    Simulation and analysis tools to evaluate the impact of atmospheric refraction on inter-satellite links.

All directories contain their own README files with further information.
