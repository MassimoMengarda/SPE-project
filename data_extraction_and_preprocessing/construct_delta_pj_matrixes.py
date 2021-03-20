import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz

from utils import get_dates_from_input_dir

def main():
    parser = argparse.ArgumentParser(description="Construct the delta pj matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("index_directory", type=str, help="the directory where the poi index matrix is stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        sys.exit("Input directory is not a directory")
    
    poi_idx_filename = os.path.join(index_dir, "poi_indexes.csv")

    if not os.path.isfile(poi_idx_filename):
        sys.exit("The given indexes directory do not contain the valid index file")
    
    os.makedirs(output_dir, exist_ok=True)

    poi_idx_file = pd.read_csv(poi_idx_filename)
    
    pattern_files = get_dates_from_input_dir(input_dir)

    if len(pattern_files) == 0:
        sys.exit("Given input directory do not contain any CSV file")
    
    poi_categories_path = os.path.join(index_dir, "poi_categories.csv")

    if not os.path.isfile(poi_categories_path):
        sys.exit("The given indexes directory do not contain the valid poi categories file")

    poi_categories_df = pd.read_csv(poi_categories_path)
    categories = pd.unique(poi_categories_df["top_category"])
    categories = categories[~pd.isnull(categories)]
    
    for filename, pattern_file in pattern_files:
        print("Reading CSV file", pattern_file)
        df = pd.read_csv(pattern_file)

        reduced_df = pd.DataFrame(data={"poi": df["safegraph_place_id"], "median_dwell": df["median_dwell"]})
        merged_df = pd.merge(poi_idx_file, reduced_df, on="poi", how="left")
        merged_df["median_dwell"].fillna(0.0, inplace=True)
        is_zero = merged_df["median_dwell"] == 0.0
        merged_df["median_dwell"] = merged_df["median_dwell"] + is_zero * sys.float_info.epsilon

        merged_df["median_dwell"] = merged_df["median_dwell"] / 60
        delta_pj_matrix = merged_df["median_dwell"].to_numpy()

        # Each outlier is set to the 90th percentile
        for category in categories:
            this_category = poi_categories_df["top_category"] == category
            quantile_90th = np.quantile(delta_pj_matrix[this_category], 0.9)
            delta_pj_matrix[np.logical_and(this_category, delta_pj_matrix > quantile_90th)] = quantile_90th

        output_filepath = os.path.join(output_dir, os.path.splitext(filename)[0])
        print("Writing file", output_filepath)
        np.save(output_filepath, delta_pj_matrix)

if __name__ == "__main__":
    main()
