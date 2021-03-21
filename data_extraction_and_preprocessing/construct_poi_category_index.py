import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, read_csv

def main(core_poi_filepath, index_dir):
    matrix_poi_df = read_csv(os.path.join(index_dir, "poi_indexes.csv"))
    core_poi_file = read_csv(core_poi_filepath)

    reduce_df = pd.DataFrame(data={"poi": core_poi_file["safegraph_place_id"], "top_category": core_poi_file["top_category"], "sub_category": core_poi_file["sub_category"]})
    merged_df = pd.merge(matrix_poi_df, reduce_df, on="poi", how="left")

    output_path = os.path.join(index_dir, "poi_categories.csv")
    print("Writing csv", output_path)
    merged_df.to_csv(output_path, index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the poi category matrix")
    parser.add_argument("index_directory", type=str, help="the directory where store the resulted index")
    parser.add_argument("input_corepoi", type=str, help="the path to the core-poi file")
    args = parser.parse_args()
    index_dir = args.index_directory
    core_poi_filepath = args.input_corepoi

    main(index_dir, core_poi_filepath)
