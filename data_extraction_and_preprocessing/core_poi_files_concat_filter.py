import argparse
import sys
import os

import pandas as pd

from utils import get_dates_from_input_dir, read_csv

def main(input_dir, zip_codes_filepath, output_filename):
    paths = get_dates_from_input_dir(input_dir)
    dfs = [read_csv(path, converters={"postal_code": str}) for path in paths]
    zip_codes = read_csv(zip_codes_filepath, converters={"zip_code": str})

    print("Concatenating files")
    final_df = pd.concat(dfs)

    print("Filtering merge file")
    final_df["postal_code"] = final_df["postal_code"].apply(lambda x: x.zfill(5))

    is_metro_area = final_df["postal_code"].isin(zip_codes["zip_code"])
    final_df = final_df[is_metro_area]

    print("Writing csv file", output_filename)
    final_df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate all the core poi files and filter them by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the core poi files are stored")
    parser.add_argument("zip_codes_filepath", type=str, help="the path to where ny metro area zip codes file is stored")
    parser.add_argument("output_filename", type=str, help="the path where to save the result")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_codes_filepath = args.zip_codes_filepath
    output_filename = args.output_filename

    main(input_dir, zip_codes_filepath, output_filename)
