import argparse
import sys
import os

import pandas as pd

from utils import get_dates_from_input_dir, read_csv

def main(input_dir, zip_cbg_filename, output_dir):
    paths = get_dates_from_input_dir(input_dir)
    zip_code_cbg_map = read_csv(zip_cbg_filename, converters={"zip_code": str, "cbg": str})
    os.makedirs(output_dir, exist_ok=True)
    

    for filename, path in paths:
        df = read_csv(path, converters={"origin_census_block_group": str})
        is_metro_area = df["origin_census_block_group"].isin(zip_code_cbg_map["cbg"])
        final_df = df[is_metro_area]

        output_filename = os.path.join(output_dir, filename)
        print("Writing csv file", output_filename)
        final_df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter all social distancing by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the social distancing files are stored")
    parser.add_argument("zip_cbg_filename", type=str, help="the path to where zip cbg file is stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_cbg_filename = args.zip_cbg_filename
    output_dir = args.output_directory
    
    main(input_dir, zip_cbg_filename, output_dir)
