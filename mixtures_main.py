import pandas as pd
import numpy as np
import argparse
import sys


def extractor(input_csv): 
    #Extracts data from input csv file
    data = pd.read_csv(input_csv)

    # Converts 'Concentrations' column to numeric values
    data['Concentrations (mM)'] = data['Concentrations (mM)'].apply(lambda x: pd.to_numeric(x.split(', '), errors='coerce') if isinstance(x, str) else np.nan)

    # Checks for missing or not valid concentration values
    if data['Concentrations (mM)'].apply(lambda x: np.isnan(x).any()).any():
        raise ValueError("One or more concentration values are missing or invalid. Please check the 'Concentrations' column in the input CSV file.")

    # Sort data if it's source liquid or desired mixture
    source_liquids = data[data['Type'] == 'Source']
    desired_mixtures = data[data['Type'] == 'Mixture']

    return source_liquids, desired_mixtures


def calculate_volumes(source_liquids, desired_mixtures):
    """
    Calculates volumes of source liquids needed for the desired mixture (based on desired concentrations and final volume).
    Parameters: source_liquids (DataFrame): Dataframe with components and concentrations of source liquids.
        desired_mixtures (DataFrame): Dataframe with components, concentrations, and final volume of desired mixtures.
    Returns:Volumes of source liquids for each desired mixture.
    Raises:ValueError: If component concentration in a source liquid is missing or multiple concentrations are found.
    """
    
    volumes_and_wells = []
    for _, mixture in desired_mixtures.iterrows():
        # Extract components, concentrations, and final volume for each desired mixture
        components = mixture['Components'].split(', ')
        concentrations = mixture['Concentrations (mM)']
        final_volume = mixture['Final Volume (ul)']

        volumes = []
        total_volume = 0

        # Calculate required volume of each source liquid needed in the mixture
        for component, concentration in zip(components, concentrations):
            #Get conc of the source liquid for the current component
            source_concentration = source_liquids.loc[source_liquids['Components'] == component, 'Concentrations (mM)'].values
            source_concentration = source_concentration[0]
            
            #Caluclate volume of the source liquid needed (C1V1 = C2V2)
            volume = (float(concentration) / float(source_concentration[0])) * final_volume
            volumes.append(volume)
            total_volume += volume

        # Add the volume of water that makes up the final volume
        volumes.append(final_volume - total_volume)
        volumes_and_wells.append(volumes)
    
    return volumes_and_wells


def get_plate_layout(plate_format):
    """
    Geneates an alphanumeric list of lists (layout) of a specified plate format, either '24-well', '96-well', or '384-well'.
    Outputs: list of lists: Plate layout containing well positions.
    Raises: ValueError: If an invalid plate format is specified.
    """

    #Generate list of lists for each plate (sequential unicode)
    if plate_format == '24-well':
        return [[f'{chr(65 + i)}{j+1}' for j in range(6)] for i in range(4)]
    elif plate_format == '96-well':
        return [[f'{chr(65 + i)}{j+1}' for j in range(12)] for i in range(8)]
    elif plate_format == '384-well':
        return [[f'{chr(65 + i)}{j+1}' for j in range(24)] for i in range(16)]
    else:
        raise ValueError("Invalid plate format specified.")

    return plate_layout


def assign_wells(volumes_and_wells, plate_format, order):
    """
    This function assigns the calculated resulting mixture and required volumes to a well in a microtiter plate.
    Inputs:
        volumes_and_wells (list of tuples): A list containing tuples of calculated resulting mixture and required volumes.
        plate_format (str): The format of the microtiter plate. Can be '24-well', '96-well', or '384-well'.
        order (str): The order in which the mixtures are assigned to the plate. Can be 'by row', 'by column', 'snake by row', or 'snake by column'.

    Returns: list of tuples: A list of tuples containing the assigned mixture volumes and corresponding wells.
    Raises ValueError: If the total number of mixture samples exceeds the capacity of the microtiter plate.
    """

    plate_layout = get_plate_layout(plate_format)
    assigned_wells = [] #Initiate list for assigned wells

    row_index = 0
    col_index = 0

    rows = len(plate_layout)
    cols = len(plate_layout[0])
    plate_size = rows * cols #total number of wells.
    total_volumes = len(volumes_and_wells) #total number of mixture samples to assign.
    
    if total_volumes > plate_size:
        raise ValueError(f"The plate size you are using is {plate_size}, "
                        f"while the total number of mixture samples is {total_volumes}. "
                        f"You will need more than one plate or another type of plate "
                        f"to run this amount of mixture samples.")

    for volumes in volumes_and_wells:
        well = plate_layout[row_index][col_index] 
        assigned_wells.append((volumes, well))
        
        if order == 'by row': #Assigns through row adding new col, starts again in first col at last row.
            col_index += 1
            if col_index == cols:
                col_index = 0
                row_index += 1
        
        elif order == 'by column':  #Assigns through col adding new row, starts again in first row at last col.
            row_index += 1
            if row_index == rows:
                row_index = 0
                col_index += 1

        elif order == 'snake by row': #Same as by row but odd rows add col in forward direction, even rows substracts col:
            if row_index % 2 == 0:  # If row is even
                col_index += 1
                if col_index == cols:  
                    col_index = cols - 1  
                    row_index += 1
            else:  # if row is odd
                col_index -= 1
                if col_index < 0: # If reached beginning of row, move to the next row
                    col_index = 0  
                    row_index += 1
            if row_index == rows: # If reached last row, move to the next col
                row_index = rows - 1
                col_index += 1
       
        elif order == 'snake by column': #Same logic than snake by row but for columns
            if col_index % 2 == 0:  # Even column
                row_index += 1
                if row_index == rows: 
                    row_index = rows - 1 
                    col_index += 1
            else:  # Odd column
                row_index -= 1
                if row_index < 0: 
                    row_index = 0 
                    col_index += 1
            if col_index == cols:
                col_index = cols - 1
                row_index += 1
                
    return assigned_wells


def write_results(output_csv, assigned_wells, desired_mixtures):
    """
    For each mixture, writes a list of source-liquid volumes (in µl) to be mixed along with the target well.
    """

    with open(output_csv, 'w') as file:
        file.write("Mixture,Target Well\n")
        
        for i, (volumes, well) in enumerate(assigned_wells):
            components = volumes[:-1]
            water_volume = volumes[-1]
            components_info = ' + '.join([f'{v:.2f} uL {c}' for v, c in zip(components, desired_mixtures.iloc[i]['Components'].split(', '))])
            mix_info = f"{components_info} + {water_volume:.2f} uL Water, {well}"
            file.write(f"{mix_info}\n")


def main(input_csv, plate_format, order, output_csv):
    """
    Main function to execute the workflow of assigning mixtures to wells in a microtiter plate.
        input_csv (str): The filename of the input CSV file.
        plate_format (str): Either '24-well', '96-well', or '384-well'.
        order (str): Either 'by row', 'by column', 'snake by row', or 'snake by column'.
        output_csv (str): The filename of the output CSV file.
    """
    source_liquids, desired_mixtures = extractor(input_csv)
    volumes_and_wells = calculate_volumes(source_liquids, desired_mixtures)
    assigned_wells = assign_wells(volumes_and_wells, plate_format, order)
    write_results(output_csv, assigned_wells, desired_mixtures)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Computes volumes of source liquids needed to make required mixture and assign them well locations of well-plate.")
    parser.add_argument("input_csv", help="Path to the combined input CSV file.")
    parser.add_argument("plate_format", choices=["24-well", "96-well", "384-well"], help="Plate format (24-well, 96-well, or 384-well).")
    parser.add_argument("order", choices=["by column", "by row", "snake by column", "snake by row"], help="Mixture order corresponds to well location.")
    parser.add_argument("output_csv", help="Path to the output CSV file.")

    args = parser.parse_args()

    main(args.input_csv, args.plate_format, args.order, args.output_csv)




