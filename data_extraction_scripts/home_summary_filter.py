import sys
import os

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 home_summary_filter.py <input directory> <zip cbg join filename> <output directory>")
    
    input_directory = sys.argv[1]
    zip_cbg_filename = sys.argv[2]
    output_directory = sys.argv[3]

    if not os.path.isdir(input_directory):
        sys.exit(f"Error: {input_directory} is not a valid directory")

    if not os.path.isdir(output_directory):
        sys.exit(f"Error: {output_directory} is not a valid directory")
    
    paths = [(filename, os.path.join(input_directory, filename)) for filename in os.listdir(input_directory) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_directory}")
    
    print("Reading csv file", zip_cbg_filename)
    zip_code_cbg_map = pd.read_csv(zip_cbg_filename, converters={"zip_code": str, "cbg": str})

    for filename, path in paths:
        print("Reading csv file", path)
        df = pd.read_csv(path, converters={"census_block_group": str})
        is_metro_area = df["census_block_group"].isin(zip_code_cbg_map["cbg"])
        final_df = df[is_metro_area]

        output_filename = os.path.join(output_directory, filename)
        print("Writing csv file", output_filename)
        final_df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
