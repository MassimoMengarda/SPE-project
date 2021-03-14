import sys
import os

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 clean_cbg_zip_table.py <input filepath> <zip in metro area filepath> <output filepath>")
    
    input_filepath = sys.argv[1]
    zip_in_metro_area_filepath = sys.argv[2]
    output_filepath = sys.argv[3]

    if not os.path.isfile(input_filepath):
        sys.exit(f"Error: {input_filepath} is not a valid file")

    if not os.path.isfile(zip_in_metro_area_filepath):
        sys.exit(f"Error: {zip_in_metro_area_filepath} is not a valid file")
    
    print("Reading csv file", zip_in_metro_area_filepath)
    zip_in_metro_df = pd.read_csv(zip_in_metro_area_filepath, converters={"zip_code":str})
    
    print("Reading csv file", input_filepath)
    zip_cbg_df = pd.read_csv(input_filepath, converters={"zip":str, "cbg":str})

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
