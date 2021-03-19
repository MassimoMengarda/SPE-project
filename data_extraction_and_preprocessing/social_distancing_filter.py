import argparse
import sys
import os

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Filter all social distancing by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the social distancing files are stored")
    parser.add_argument("zip_cbg_filename", type=str, help="the path to where zip cbg file is stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_cbg_filename = args.zip_cbg_filename
    output_directory = args.output_directory

    if not os.path.isdir(input_dir):
        sys.exit(f"Error: {input_dir} is not a valid directory")

    if not os.path.isdir(output_directory):
        sys.exit(f"Error: {output_directory} is not a valid directory")
    
    paths = [(filename, os.path.join(input_dir, filename)) for filename in os.listdir(input_dir) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_dir}")
    
    print("Reading csv file", zip_cbg_filename)
    zip_code_cbg_map = pd.read_csv(zip_cbg_filename, converters={"zip_code": str, "cbg": str})

    for filename, path in paths:
        print("Reading csv file", path)
        df = pd.read_csv(path, converters={"origin_census_block_group": str})
        is_metro_area = df["origin_census_block_group"].isin(zip_code_cbg_map["cbg"])
        final_df = df[is_metro_area]

        output_filename = os.path.join(output_directory, filename)
        print("Writing csv file", output_filename)
        final_df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
