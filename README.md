# **Mixture Assigner** 

## Description

This Python script (`mixtures_main.py`) computes the volumes of source liquids that are needed to create a series of required dilution mixtures, and assigns them to well locations on a microtiter plate.

## Installation

Clone this repository to your local machine.
Ensure you have Python installed.
Install required packages using pip install -r requirements.txt.

## Usage

Run the script with the following command:

</br>


> `python mixtures_main.py input_csv plate_format order output_csv`

</br>


- `input_csv`: Path to the combined input CSV file.
- `plate_format`: Plate format (24-well, 96-well, or 384-well).
- `order`: How mixture order is mapped onto plate (write in quotations "by column", "by row", "snake by column", or "snake by row").
- `output_csv`: Path to the output CSV file.

### Use example

</br>

> `python mixtures_main.py input.csv 96-well "by row" output.csv`

</br>

## Input CSV Format

The input CSV should have the following columns:

- **Type**: Type of liquid (Either "Source" or "Mixture").
- **Components**: Components of the liquid. If a mixture, separate components by commas (i.e NaCl, EDTA, DMSO)
- **Concentrations (mM)**: Concentrations of components. If a mixture, separate desired concentrations by commas (i.e 10, 100, 10).
- **Final Volume (ul)**: The desired final volume for the mixture.

</br>

## Output CSV Format

</br>

The output CSV contains the assigned mixture volumes and corresponding wells.

</br>

## Dependencies

pandas

numpy

argparse
