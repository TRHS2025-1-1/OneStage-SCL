import pandas as pd
import os
from tqdm import tqdm

name_list = ['fan', 'pump', 'slider', 'ToyCar', 'ToyConveyor', 'valve']

for name in name_list:
    # Read the CSV file
    df = pd.read_csv(f'{name}.csv', header=None)
    df.columns = ['filename', 'dummy', 'label']

    # Create a mapping dictionary
    label_mapping = {row['filename']: row['label'] for idx, row in df.iterrows()}

    # Get the folder path
    folder_path = f'{name}/test/'

    # Iterate over the files in the directory
    file_list = os.listdir(folder_path)

    # Use tqdm to display a progress bar
    for filename in tqdm(file_list, desc=f"Processing Machine {name}"):
        if filename in label_mapping:
            # Get the label
            label = label_mapping[filename]
            # Construct the new filename
            if label == 0:
                new_filename = 'normal_' + filename
            else:
                new_filename = 'anomaly_' + filename
            # Construct the full paths
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            # Rename the file
            os.rename(old_file, new_file)

print("Renaming completed.")
