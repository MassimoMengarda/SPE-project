import argparse
import sys
import os

import pandas as pd

from ..utils import read_csv

def main(input_dir, zip_cbg_filename, output_dir):
    paths = [(filename, os.path.join(data_directory, filename)) for filename in os.listdir(data_directory) if filename.endswith(".csv") and filename != "cbg_patterns.csv"]
    fields = read_csv(os.path.join(input_dir, "metadata", "cbg_field_descriptions.csv"))
    df = read_csv(os.path.join(input_dir, "data", "cbg_patterns.csv"), converters={"census_block_group": str})
    zip_code_cbg_map = read_csv(zip_cbg_filename, converters={"zip_code": str, "cbg": str})

    fields_mapping = pd.Series(fields["field_full_name"].values,index=fields["table_id"]).to_dict()

    is_metro_area = df["census_block_group"].isin(zip_code_cbg_map["cbg"])
    df = df[is_metro_area]

    cbg_patterns_output_filename = os.path.join(output_dir, "cbg_patterns.csv")
    df.to_csv(cbg_patterns_output_filename, index=False)
    
    for filename, path in paths:
        df = read_csv(path, converters={"census_block_group": str})
        is_metro_area = df["census_block_group"].isin(zip_code_cbg_map["cbg"])
        df = df[is_metro_area]

        df.rename(columns=fields_mapping, inplace=True)

        output_filename = os.path.join(output_dir, filename)
        print("Writing csv file", output_filename)
        df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter all population files by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the population files are stored")
    parser.add_argument("zip_cbg_filename", type=str, help="the path to where zip cbg file is stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_cbg_filename = args.zip_cbg_filename
    output_dir = args.output_directory

    main(input_dir, zip_cbg_filename, output_dir)
