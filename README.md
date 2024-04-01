# **Dilution Microwell plate assigner** 

## Description

This Python script (`mixtures_main.py`) computes the volumes of source liquids that are needed to create a series of required dilution mixtures, and assigns them to well locations on a desired microtiter plate (24-well, 96-well and 384-well plate), and in a specified order (by row, by column or snaking by either). If wanted, it also outputs a well map of the resulting plate layout, for record keeping. 


## Installation

- Clone this repository to your local path.
- Ensure you have Python installed.
- Install required packages using:

`pip install -r requirements.txt`

## Usage

In your terminal type the following general command to run the script:

</br>


`python mixtures_main.py input_csv plate_format order output_csv`

</br>

Where:

</br>

- `input_csv`: Replace with the path to your input CSV file (see requirements below).
- `plate_format`: Replace with either of the following plate formats: 24-well, 96-well, or 384-well.
- `order`: Replace by how you want your mixtures to be ordered in the microwell plate (write in quotations "by column", "by row", "snake by column", or "snake by row").
- `output_csv`: Replace with the path and new file name for your output CSV file.

</br>

A prompt will also ask wether you require an image map of the resulting plate layout. Respond with yes or no, and if yes provide a name for the image file. 

</br>

### Use example

`python mixtures_main.py sample_input.csv 96-well "by row" sample_output2.csv`

</br>

This command will analyse the input.csv file and map the mixtures to a 96-well plate by row (A1, A2, A3...). The script will generate the "output.csv" file with the results, as shown in the input/output examples below. 

</br>

## Input CSV Format

Your input CSV should have the following columns, typed exaclty as:

- **Type**: Type of liquid (Either "Source" or "Mixture").
- **Components**: Components of the source and mixtures. If a mixture, separate the components by commas (i.e NaCl, EDTA, DMSO)
- **Concentrations (mM)**: Concentrations of the components, in millimolar (mM). If a mixture, separate desired concentrations by commas in their corresponding order (i.e 10, 100, 10).
- **Final Volume (ul)**: The desired final volume for the mixture, in microliters (ul).

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

This script will also output a .png image of the corresponding layout. 

</br>

|Mixture Number|Mixture                                                    |Target Well|
|--------------|-----------------------------------------------------------|-----------|
|1             |1.00 uL Na + 10.00 uL Cl + 89.00 uL Water                  |A1         |
|2             |1.00 uL Na + 10.00 uL Cl + 89.00 uL Water                  |A2         |
|3             |10.00 uL Na + 5.00 uL EDTA + 85.00 uL Water                |A3         |
|4             |10.00 uL Na + 1.00 uL Cl + 0.50 uL EDTA + 88.50 uL Water   |A4         |
|5             |100.00 uL Na + 10.00 uL Cl + 5.00 uL EDTA + 885.00 uL Water|A5         |
|6             |100.00 uL Na + 10.00 uL Cl + 5.00 uL EDTA + 885.00 uL Water|A6         |
|7             |100.00 uL Na + 10.00 uL Cl + 0.50 uL EDTA + 889.50 uL Water|B1         |



</br>

## Optional quick layout image

<img src="https://github.com/GuadalupeAlvarezGonzalez/Microplate-Task/assets/129006181/1bc0253c-851c-4cc2-868b-21bb124a876e" width="500" />

</br>
