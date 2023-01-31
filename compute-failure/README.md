# Radiation Testing

## Total Ionizing Dose (TID)

We calculate the total ionizing dose for a component on a spacecraft in a circular
orbit in LEO.
We assume an altitude of 550km (approx. the Starlink altitude for most shells).
Here's how we calculate the TID:

1. Create a ESA Space Weather Service Network (ESA-SWE) account

    1. Go to [ESA-SWE Registration](https://swe.ssa.esa.int/registration)
    1. Fill out the account registration form
    1. Confirm your account via email

1. Access the Space Environment Information System (SPENVIS)

    1. Go to [ESA-SWE SPENVIS](https://spenvis.ssa-swe.eu/)
    1. Log in
    1. Click "Access"
    1. Create a new project

1. For each of the inclinations [0deg, 180deg] (5deg interval), complete the following steps:

    1. Generate Coordinates

        1. Go to "Coordinate Generators"
        1. Go to "Spacecraft trajectories"
        1. Set mission duration "5.0 years"
        1. Click "Next"
        1. Set orbit start to 01 January 2023
        1. Set "Representative trajectory duration" to "30"
        1. Set "Altitude specification" to "circular orbit"
        1. Set "Altitude [km]" to "550"
        1. Set "Inclination" to your inclination
        1. Click "Next"
        1. Click "Run"

        Your project now has trajectory information.

    1. Generate radiation sources

        1. Click "Radiation sources and effects"
        1. Click "Trapped proton and electron fluxes"
        1. Select "AP-8" as a proton model and "solar minimum" (this will use AP8-MIN, as proton fluxes are highest at solar minimum)
        1. Select "AE-8" as an electron model and "solar maximum" (this will use AE8-MIN, as electron fluxes are highest at solar maximum)
        1. Click "Run"

    1. Generate ionizing dose

        1. Click "Radiation sources and effects"
        1. Click "Ionizing dose for simple geometries"
        1. Select "SHIELDOSE-2"
        1. Set "Shielding configuration" to "centre of AI spheres"
        1. Set "Target material" to "Silicon"
        1. Click "Run"

    1. Save Results

        1. Click "SHIELDOSE-2 Doses"
        1. Copy to a new file named "[inclination].txt"
        1. GOTO TOP
