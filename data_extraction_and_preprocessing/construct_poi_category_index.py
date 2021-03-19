import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir

def main():
    parser = argparse.ArgumentParser(description="Construct the poi category matrix")
    parser.add_argument("input_corepoi", type=str, help="the path to the core-poi file")
    parser.add_argument("index_directory", type=str, help="the directory where store the resulted index")
    args = parser.parse_args()
    core_poi_filename = args.input_corepoi
    index_directory = args.index_directory

    if not os.path.isfile(core_poi_filename):
        sys.exit("The given path to core-poi file is not valid")
    
    matrix_poi_filename = os.path.join(index_directory, "poi_indexes.csv")

    if not os.path.isfile(matrix_poi_filename):
        sys.exit(f"{matrix_poi_filename} is not valid a valid matrix poi file path")

    print("Reading csv", matrix_poi_filename)
    matrix_poi_df = pd.read_csv(matrix_poi_filename)

    print("Reading csv", core_poi_filename)
    core_poi_file = pd.read_csv(core_poi_filename)

    reduce_df = pd.DataFrame(data={"poi": core_poi_file["safegraph_place_id"], "top_category": core_poi_file["top_category"], "sub_category": core_poi_file["sub_category"]})
    merged_df = pd.merge(matrix_poi_df, reduce_df, on="poi", how="left")

    output_path = os.path.join(index_directory, "poi_categories.csv")
    print("Writing csv", output_path)
    merged_df.to_csv(output_path, index=False)
    
if __name__ == "__main__":
    main()
