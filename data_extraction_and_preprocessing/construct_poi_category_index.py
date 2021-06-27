import argparse
import os

import pandas as pd

from utils import read_csv

def main(info_dir, core_poi_filepath):
    matrix_poi_df = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    core_poi_file = read_csv(core_poi_filepath)

    reduce_df = pd.DataFrame(data={"poi": core_poi_file["safegraph_place_id"], "top_category": core_poi_file["top_category"], "sub_category": core_poi_file["sub_category"]})
    merged_df = pd.merge(matrix_poi_df, reduce_df, on="poi", how="left")

    output_path = os.path.join(info_dir, "poi_categories.csv")
    print("Writing csv", output_path)
    merged_df.to_csv(output_path, index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the poi category matrix")
    parser.add_argument("info_directory", type=str, help="the directory where store the resulted index")
    parser.add_argument("core_poi_filepath", type=str, help="the path to the core-poi file")
    args = parser.parse_args()
    info_dir = args.info_directory
    core_poi_filepath = args.core_poi_filepath

    main(info_dir, core_poi_filepath)
