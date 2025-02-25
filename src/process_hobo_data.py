import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Define a function to process each file
def process_hobo_files(folder_path):
    # Initialize an empty list to store data
    data = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            # Extract the device number from the filename
            device = filename.split()[0]

            # Construct the full path to the file
            file_path = os.path.join(folder_path, filename)

            # Read the CSV file
            df = pd.read_csv(file_path)

            # Keep only the necessary columns by index (2nd and 3rd columns) and rename them
            df = df.iloc[:, [1, 2]]
            df.columns = ['time', 'temp']

            # Add the device column
            df['device'] = device

            # Drop rows where 'reading' is NaN
            df = df.dropna(subset=['temp'])

            # Append the DataFrame to the list
            data.append(df)

    # Concatenate all data into a single DataFrame
    final_df = pd.concat(data, ignore_index=True)

    return final_df

# Specify the folder containing your HOBO files
folder_path = "data/HOBO_data/fwdtgttrial5"

# Process the files
result_df = process_hobo_files(folder_path)

# Display the resulting DataFrame
#how many unqiue devices are there?
gussets = pd.read_csv("data/gusset_map_table1.csv")
result_df = result_df.merge(gussets, on='device', how='left')

print(result_df)


# Optionally, save the DataFrame to a CSV file
result_df.to_csv("data/compiled_hobo_data.csv", index=False)

