import sys
import os

import pandas as pd

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: PATH/python3 core_poi_files_merge.py <input directory> <output filename>")
    
    input_directory = sys.argv[1]
    output_filename = sys.argv[2]

    if not os.path.isdir(input_directory):
        sys.exit(f"Error: {input_directory} is not a valid directory")
    
    paths = [os.path.join(input_directory, filename) for filename in os.listdir(input_directory) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_directory}")
    
    dfs = []
    for path in paths:
        print("Reading csv file", path)
        dfs.append(pd.read_csv(path))
    
    print("Concatenating files")
    final_df = pd.concat(dfs)

    print(final_df)

    print("Writing csv file", output_filename)
    final_df.to_csv(output_filename, index = False)


if __name__ == "__main__":
    main()