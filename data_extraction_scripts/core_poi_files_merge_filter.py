import sys
import os

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 core_poi_files_merge_filter.py <input directory> <metro area postal codes input filename> <output filename>")
    
    input_directory = sys.argv[1]
    zip_codes_filepath = sys.argv[2]
    output_filename = sys.argv[3]

    if not os.path.isdir(input_directory):
        sys.exit(f"Error: {input_directory} is not a valid directory")
    
    paths = [os.path.join(input_directory, filename) for filename in os.listdir(input_directory) if filename.endswith(".csv")]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {input_directory}")
    
    dfs = []
    for path in paths:
        print("Reading csv file", path)
        dfs.append(pd.read_csv(path, converters={"postal_code": str}))
    
    print("Concatenating files")
    final_df = pd.concat(dfs)

    print("Reading csv file", zip_codes_filepath)
    zip_codes = pd.read_csv(path, converters={"zip_code": str})

    print("Filtering merge file")
    final_df["postal_code"] = final_df["postal_code"].apply(lambda x: x.zfill(5))

    is_metro_area = final_df["postal_code"].isin(zip_codes["zip_code"])
    final_df = final_df[is_metro_area]

    print("Writing csv file", output_filename)
    final_df.to_csv(output_filename, index = False)


if __name__ == "__main__":
    main()