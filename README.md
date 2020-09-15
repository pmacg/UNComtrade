# UNComtrade
Some Python scripts which are useful for the UN Comtrade dataset. Not complete at the moment, will add more funcionality over time. Code mostly meant as started code at the moment, feel free to implement your own functionalities and PR :)

In `./data/` I've included 2 folders of cleaned up csv files for both oil (HS code 27) and wood (HS code 44) for 1988-2017.

## Installation
Install needed packages using conda: `conda env create -f environment.yml`

## How to Use
To create the adjacency matrix: `python3 create_adjacency_matrix.py <commodity> <year> <output_file>`
Where commodity can be one of "oil" or "wood", year should be between 1988 and 2017, and output_file is the name of the file you would like the script to save the adjacency matrix to.

The script will save the matrix in the numpy `.npy` format to the file specified on the command line.
This can be loaded into another script using the `numpy.load()` method.

## Information
Information about the UN comtrade dataset can be found here: https://comtrade.un.org/

I've also written about the UN Comtrade database in Chapter 4 of my MSc thesis here. Section 4.1 in particular should help explain the UN Comtrade dataset: https://project-archive.inf.ed.ac.uk/msc/20193694/msc_proj.pdf
