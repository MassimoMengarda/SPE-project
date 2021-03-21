import argparse
import sys

import pandas as pd

from utils import read_csv

def main(input_filepath, output_filepath):
    df = read_csv(input_filepath, converters={"zip_code": str})

    print("Filtering file")
    new_df = df.drop_duplicates(subset = ["zip_code"])

    print("Writing csv file", output_filepath)
    new_df.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean the duplicated zip codes")
    parser.add_argument("input_filepath", type=str, help="the path to the zip table file")
    parser.add_argument("output_filepath", type=str, help="the path where to save the result")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    output_filepath = args.output_filepath

    main(input_filepath, output_filepath)

