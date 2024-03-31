import pandas as pd
import numpy as np
import argparse
import sys
import os


def extractor(input_csv): 
    """ Function to extract data from input CSV file and check for errors within input fiile.
    input_csv (str): Path to the input CSV file.
    Returns: source_liquids (DataFrame): DataFrame with components and concentrations of source liquids.
             desired_mixtures (DataFrame): DataFrame with components, concentrations, and final volume of the mixtures.
    Raises ValueError: If the input data is not in correct format or is missing/invalid data.
    """
    data = pd.read_csv(input_csv)
    
    # Check if the input CSV file exists or its correctly mapped 
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV file '{input_csv}' not found or correclty specified.")

    # Check if the required columns are present
    required_columns = ['Type', 'Components', 'Concentrations (mM)', 'Final Volume (ul)']
    if not set(required_columns).issubset(data.columns):
        raise ValueError("The input data is missing one or more required columns.")

    # Converts 'Concentrations' column to numeric values, and checks if theres missing data or invalid
    data['Concentrations (mM)'] = data['Concentrations (mM)'].apply(lambda x: pd.to_numeric(x.split(', '), errors='coerce') if isinstance(x, str) else np.nan)
    if data['Concentrations (mM)'].apply(lambda x: np.isnan(x).any()).any():
        raise ValueError("One or more concentration are missing or invalid. Please check the 'Concentrations' column in your input CSV file.")

    # Differentiates data as source liquid or desired mixture
    source_liquids = data[data['Type'] == 'Source']
    desired_mixtures = data[data['Type'] == 'Mixture']

    return source_liquids, desired_mixtures


def calculate_volumes(source_liquids, desired_mixtures):
    """ Calculates volumes of source liquids needed for the desired mixture (based on desired concentrations and final volume).
    Parameters: source_liquids (DataFrame): Dataframe with components and concentrations of source liquids.
                desired_mixtures (DataFrame): Dataframe with components, concentrations, and final volume of desired mixtures.
    Returns: A list containing tuples of calculated resulting mixture and required volumes.
    Raises:ValueError: If the concentration of a mixture component is higher than the stock. 
    """

    all_mixture_volumes = []

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

        volumes.append(final_volume - total_volume)
        all_mixture_volumes.append(volumes)
        
    # Check if any mixture concentrations are higher than source liquid concentrations
    source_liquids_dict = dict(zip(source_liquids['Components'], source_liquids['Concentrations (mM)']))
    for index, row in desired_mixtures.iterrows():
        concentrations = [float(c) for c in row['Concentrations (mM)']]
        components = row['Components'].split(', ')
        for component, concentration in zip(components, concentrations):
            if concentration > source_liquids_dict.get(component, 0):
                raise ValueError(f"The concentration of '{component}' in one or more of the mixture(s) is higher than the source liquid!!")


    return all_mixture_volumes


def get_plate_layout(plate_format):
    """ Geneates an alphanumeric list of lists (layout) of a specified plate format, either '24-well', '96-well', or '384-well'.
    Outputs list of lists: Plate layout containing well positions.
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
        raise ValueError("Would be nice but this plate layout does not exsist. Please choose either '24-well', '96-well', or '384-well'.")

    return plate_layout



def assign_wells(all_mixture_volumes, plate_format, order): # This is the fun function ✨
    """ This function assigns eachn mixture to a well in a microtiter plate, according to a specified order.
    Inputs: all_mixture_volumes (list of tuples): A list containing tuples of calculated resulting mixture and required volumes.
            plate_format (str): The format of the microtiter plate. Can be '24-well', '96-well', or '384-well'.
            order (str): The order in which the mixtures are assigned to the plate. Can be 'by row', 'by column', 'snake by row', or 'snake by column'.
    Returns: list of tuples: A list of tuples containing the assigned mixture volumes and corresponding wells.
    Raises ValueError: If the total number of mixture samples exceeds the number of wells in the specified microtiter plate.
    """

    plate_layout = get_plate_layout(plate_format)
    assigned_wells = [] #Initiate list for assigned wells

    row_index = 0
    col_index = 0

    rows = len(plate_layout)
    cols = len(plate_layout[0])
    plate_size = rows * cols #total number of wells.
    total_volumes = len(all_mixture_volumes) #total number of mixture samples to assign.
    
    if total_volumes > plate_size:
        raise ValueError(f"The plate size you are using is {plate_size}, "
                        f"while the total number of mixture samples is {total_volumes}. "
                        f"You will need more than one plate or another type of plate "
                        f"to run this amount of mixture samples.")

    for volumes in all_mixture_volumes:
        well = plate_layout[row_index][col_index] 
        assigned_wells.append((volumes, well))
        
        #Assigns through row adding new col, starts again in first col at last row.
        if order == 'by row': 
            col_index += 1
            if col_index == cols:
                col_index = 0
                row_index += 1
        #Assigns through col adding new row, starts again in first row at last col.
        elif order == 'by column':  
            row_index += 1
            if row_index == rows:
                row_index = 0
                col_index += 1
        #Same as by row but odd rows add col in forward direction, even rows substracts:
        elif order == 'snake by row': 
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
       #Same logic than snake by row but for columns
        elif order == 'snake by column': 
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
            else:
                raise ValueError(f"Invalid order specified. Please choose one of the supported orders: "
                                f"'by row', 'by column', 'snake by row', or 'snake by column'")
    
    return assigned_wells


def write_results(output_csv, assigned_wells, desired_mixtures):
    """ For each mixture, writes a CSV output file containing a list of source-liquid volumes (in µl) 
    to be mixed along with the target well.
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
    """ Main function to execute the workflow of assigning mixtures to wells in a microtiter plate.
        input_csv (str): The filename of the input CSV file.
        plate_format (str): Either '24-well', '96-well', or '384-well'.
        order (str): Either 'by row', 'by column', 'snake by row', or 'snake by column'.
        output_csv (str): The filename of the output CSV file.
    """
    source_liquids, desired_mixtures = extractor(input_csv)
    all_mixture_volumes = calculate_volumes(source_liquids, desired_mixtures)
    assigned_wells = assign_wells(all_mixture_volumes, plate_format, order)
    write_results(output_csv, assigned_wells, desired_mixtures)

    print(f"\n \n Congrats! Your mixtures output file has been written in your specified path. \n "
        f"You're now a step closer to automating your dilutions!", "\U0001F9EA", "\U0001F916" "\n \n ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Computes volumes of source liquids needed to make" 
    f"required mixture and assign them well locations in a specified well-plate.")
    parser.add_argument("input_csv", help="Path to the combined input CSV file.")
    parser.add_argument("plate_format", choices=["24-well", "96-well", "384-well"], help="Plate format (24-well, 96-well, or 384-well).")
    parser.add_argument("order", choices=["by column", "by row", "snake by column", "snake by row"], help="Mixture order corresponds to well location.")
    parser.add_argument("output_csv", help="Path to the output CSV file.")

    args = parser.parse_args()

    main(args.input_csv, args.plate_format, args.order, args.output_csv)






