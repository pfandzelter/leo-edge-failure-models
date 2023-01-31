# Failure is not an Option: Considerations for Software Fault-Tolerance in LEO Satellite Edge Computing

This repository contains experiments and simulations accompanying our paper on failure scenarios for LEO edge computing.

If you use this software in a publication, please cite it as:

### Text

T. Pfandzelter and D. Bermbach, **Failure is not an Option: Considerations for Software Fault-Tolerance in LEO Satellite Edge Computing**, 2023.

### BibTeX

```bibtex
@article{pfandzelter2023leoedgefaults,
    title = "Failure is not an Option: Considerations for Software Fault-Tolerance in LEO Satellite Edge Computing",
    author = "Pfandzelter, Tobias and Bermbach, David",
    year = 2023
}
```

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
