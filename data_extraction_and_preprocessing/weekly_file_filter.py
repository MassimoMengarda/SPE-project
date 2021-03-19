import argparse
import sys

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Filter all weekly files by zip codes")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly files files are stored")
    parser.add_argument("zip_codes_filepath", type=str, help="the path to where ny metro area zip codes file is stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_codes_filepath = args.zip_codes_filepath
    output_directory = args.output_directory

    if not os.path.isdir(input_dir):
        sys.exit(f"Error: {input_dir} is not a valid directory")
    
    paths = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_dir}")

    if not os.path.isfile(zip_codes_filepath):
        sys.exit(f"Error: {zip_codes_filepath} is not a valid file")

    print("Reading csv file", zip_codes_filepath)
    zip_codes = pd.read_csv(zip_codes_filepath, converters={"zip_code": str})
    
    for filename, path in paths:
        print("Reading csv file", path)
        df = pd.read_csv(path, converters={"postal_code": str})

        print("Filtering file")
        df["postal_code"] = df["postal_code"].apply(lambda x: x.zfill(5))

        is_metro_area = df["postal_code"].isin(zip_codes["zip_code"])
        df_metro_area = df[is_metro_area]

        output_filename = os.path.join(output_directory, filename)
        print("Writing csv file", output_filename)
        df_metro_area.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
