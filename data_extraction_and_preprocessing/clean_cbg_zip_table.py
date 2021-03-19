import argparse
import sys
import os

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Clean the cbg zip table")
    parser.add_argument("input_filepath", type=str, help="the path to the cbg zip table file")
    parser.add_argument("zip_in_metro_area_filepath", type=str, help="the path to the zip in metro area file")
    parser.add_argument("output_filepath", type=str, help="the path where to save the result")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    zip_in_metro_area_filepath = args.zip_in_metro_area_filepath
    output_filepath = args.output_filepath

    if not os.path.isfile(input_filepath):
        sys.exit(f"Error: {input_filepath} is not a valid file")

    if not os.path.isfile(zip_in_metro_area_filepath):
        sys.exit(f"Error: {zip_in_metro_area_filepath} is not a valid file")

    print("Reading csv file", input_filepath)
    zip_cbg_df = pd.read_csv(input_filepath, converters={"zip": str, "cbg": str})
    
    print("Reading csv file", zip_in_metro_area_filepath)
    zip_in_metro_df = pd.read_csv(zip_in_metro_area_filepath, converters={"zip_code": str})

    print("Filtering data")
    is_metro_area = zip_cbg_df["zip"].isin(zip_in_metro_df["zip_code"])
    final_df = zip_cbg_df[is_metro_area]

    print(f"ZIP codes inside the metro area: {len(pd.unique(zip_in_metro_df['zip_code']))}")
    print(f"ZIP codes inside the filtered ZIP CBG mapping: {len(pd.unique(final_df['zip']))}")
    print(f"CBG codes inside the filtered ZIP CBG mapping: {len(pd.unique(final_df['cbg']))}")

    print("Writing csv file", output_filepath)
    final_df.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    main()
