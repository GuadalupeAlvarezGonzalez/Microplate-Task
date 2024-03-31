# **Mixture Assigner** 

## Description

This Python script (`mixtures_main.py`) computes the volumes of source liquids that are needed to create a series of required dilution mixtures, and assigns them to well locations on a microtiter plate.

## Installation

Clone this repository to your local machine.
Ensure you have Python installed.
Install required packages using pip install -r requirements.txt.

## Usage

Run the script with the following terminal command:

</br>


> `python mixtures_main.py input_csv plate_format order output_csv`

</br>

Where:

</br>

- `input_csv`: Path to the combined input CSV file.
- `plate_format`: Plate format (24-well, 96-well, or 384-well).
- `order`: How mixture order is mapped onto plate (write in quotations "by column", "by row", "snake by column", or "snake by row").
- `output_csv`: Path to the output CSV file.

</br>

### Use example


> `python mixtures_main.py input.csv 96-well "by row" output.csv`

</br>

## Input CSV Format

The input CSV should have the following columns:

- **Type**: Type of liquid (Either "Source" or "Mixture").
- **Components**: Components of the liquid. If a mixture, separate components by commas (i.e NaCl, EDTA, DMSO)
- **Concentrations (mM)**: Concentrations of components, in their corresponding order. If a mixture, separate desired concentrations by commas (i.e 10, 100, 10).
- **Final Volume (ul)**: The desired final volume for the mixture.

</br>

CSV Data: An example of what the data would look like in excel for three stocks and 7 different desired mixtures:


</br>


|Type   |Components  |Concentrations (mM)|Final Volume (ul)|
|-------|------------|-------------------|-----------------|
|Source |Na          |100                |                 |
|Source |Cl          |100                |                 |
|Source |EDTA        |200                |                 |
|Mixture|Na, Cl      |1, 1               |100              |
|Mixture|Na, Cl      |1, 10              |100              |
|Mixture|Na, EDTA    |10, 10             |100              |
|Mixture|Na, Cl, EDTA|10, 1, 1           |100              |
|Mixture|Na, Cl, EDTA|10, 1, 1           |1000             |
|Mixture|Na, Cl, EDTA|10, 1, 10          |1000             |
|Mixture|Na, Cl, EDTA|10, 1, 0.1         |1000             |

</br>
</br>

## Output CSV Format

</br>

The output CSV contains the assigned mixture volumes and corresponding wells. Below is an example for the output obtained when assigning the input data to a 24-well "by row".

</br>

|Mixture|Target Well|
|-------|-----------|
|1.00 uL Na + 1.00 uL Cl + 98.00 uL Water| A1        |
|1.00 uL Na + 10.00 uL Cl + 89.00 uL Water| A2        |
|10.00 uL Na + 5.00 uL EDTA + 85.00 uL Water| A3        |
|10.00 uL Na + 1.00 uL Cl + 0.50 uL EDTA + 88.50 uL Water| A4        |
|100.00 uL Na + 10.00 uL Cl + 5.00 uL EDTA + 885.00 uL Water| A5        |
|100.00 uL Na + 10.00 uL Cl + 5.00 uL EDTA + 885.00 uL Water| A6        |
|100.00 uL Na + 10.00 uL Cl + 0.50 uL EDTA + 889.50 uL Water| B1        |


</br>
