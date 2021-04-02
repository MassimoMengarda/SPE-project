import argparse
import sys
import os

import pandas as pd

from ..utils import get_dates_from_input_dir, read_csv

def main(input_dir, zip_codes_filepath, output_dir):
    paths = get_dates_from_input_dir(input_dir)
    zip_codes = read_csv(zip_codes_filepath, converters={"zip_code": str})
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, path in paths:
        df = read_csv(path, converters={"postal_code": str})

        print("Filtering file")
        df["postal_code"] = df["postal_code"].apply(lambda x: x.zfill(5))

        is_metro_area = df["postal_code"].isin(zip_codes["zip_code"])
        df_metro_area = df[is_metro_area]

        output_filename = os.path.join(output_dir, filename)
        print("Writing csv file", output_filename)
        df_metro_area.to_csv(output_filename, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter all weekly files by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly files files are stored")
    parser.add_argument("zip_codes_filepath", type=str, help="the path to where ny metro area zip codes file is stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_codes_filepath = args.zip_codes_filepath
    output_dir = args.output_directory

    main(input_dir, zip_codes_filepath, output_dir)
