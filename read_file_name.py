import os
import sys

"""
The code gives the output the name of the files inside the folders
"""

# Check if folder path is provided
if len(sys.argv) < 2:
    print("Usage: python read_file_name.py <folder_path>")
    sys.exit(1)

folder_path = sys.argv[1]

# Check if folder exists
if not os.path.isdir(folder_path):
    print("Invalid folder path")
    sys.exit(1)

# Print file names
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    if os.path.isfile(file_path):
        print(f'{{path:"../../../assets/notices/{file_name}"}}')
