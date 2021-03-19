import argparse
import sys
import os

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Concatenate all the core poi files and filter them by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the core poi files are stored")
    parser.add_argument("zip_codes_filepath", type=str, help="the path to where ny metro area zip codes file is stored")
    parser.add_argument("output_filename", type=str, help="the path where to save the result")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_codes_filepath = args.zip_codes_filepath
    output_filename = args.output_filename

    if not os.path.isdir(input_dir):
        sys.exit(f"Error: {input_dir} is not a valid directory")
    
    paths = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_dir}")
    
    dfs = []
    for path in paths:
        print("Reading csv file", path)
        dfs.append(pd.read_csv(path, converters={"postal_code": str}))
    
    print("Concatenating files")
    final_df = pd.concat(dfs)

    print("Reading csv file", zip_codes_filepath)
    zip_codes = pd.read_csv(zip_codes_filepath, converters={"zip_code": str})

    print("Filtering merge file")
    final_df["postal_code"] = final_df["postal_code"].apply(lambda x: x.zfill(5))

    is_metro_area = final_df["postal_code"].isin(zip_codes["zip_code"])
    final_df = final_df[is_metro_area]

    print("Writing csv file", output_filename)
    final_df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
