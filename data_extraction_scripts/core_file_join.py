import sys

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 core_file_join.py <core filename> <weekly filename> <output filename>")
    
    core_filename = sys.argv[1]
    weekly_filename = sys.argv[2]
    output_filename = sys.argv[3]

    print("Reading core csv file ", core_filename)
    core_filename = pd.read_csv(core_filename)
    

    print("Reading csv file", weekly_filename)
    weekly = pd.read_csv(weekly_filename, converters={"postal_code": str})
    # print(df.describe())
    # print(df.isna().sum())

    print("Filtering file")
    merged = weekly.merge(core_filename, left_on="safegraph_place_id", right_on="safegraph_place_id", how="left")

    print("Writing csv file", output_filename)
    merged.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
