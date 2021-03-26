import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz

from utils import get_dates_from_input_dir, read_csv

def main(input_dir, info_dir, output_dir):
    poi_idx_file = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    pattern_files = get_dates_from_input_dir(input_dir)
    poi_categories_df = read_csv(os.path.join(info_dir, "poi_categories.csv"))
    os.makedirs(output_dir, exist_ok=True)

    categories = pd.unique(poi_categories_df["top_category"])
    categories = categories[~pd.isnull(categories)]
    
    for filename, pattern_file in pattern_files:
        df = read_csv(pattern_file)

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
    parser = argparse.ArgumentParser(description="Construct the delta pj matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the poi index matrix is stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    info_dir = args.info_directory
    output_dir = args.output_directory

    main(input_dir, info_dir, output_dir)
