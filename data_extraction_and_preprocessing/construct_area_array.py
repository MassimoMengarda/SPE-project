import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import read_csv

def main(input_filepath, info_dir, output_filepath):
    area_file = read_csv(input_filepath)
    poi_idx_file = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    poi_categories_df = read_csv(os.path.join(info_dir, "poi_categories.csv"))

    categories = pd.unique(poi_categories_df["top_category"])
    categories = categories[~pd.isnull(categories)]

    reduced_df = pd.DataFrame(data={"poi": area_file["safegraph_place_id"], "area_square_feet": area_file["area_square_feet"]})
    merged_df = pd.merge(poi_idx_file, reduced_df, on="poi", how="left", indicator=True)
    
    print(merged_df["_merge"].value_counts())

    # Each outlier is set to the 95th and 5th percentiles
    for category in categories:
        this_category = poi_categories_df["top_category"] == category

        quantile_df = merged_df["area_square_feet"][this_category].quantile([0.05, 0.95])
        
        merged_df.loc[np.logical_and(this_category, merged_df["area_square_feet"] > quantile_df[0.95]), "area_square_feet"] = quantile_df[0.95]
        merged_df.loc[np.logical_and(this_category, merged_df["area_square_feet"] < quantile_df[0.05]), "area_square_feet"] = quantile_df[0.05]
        
        category_area_mean = merged_df["area_square_feet"].mean()
        merged_df["area_square_feet"].fillna(category_area_mean)
    
    areas_array = merged_df["area_square_feet"].to_numpy()
    print("Writing file", output_filepath)
    np.save(output_filepath, areas_array)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the POI area array")
    parser.add_argument("input_filepath", type=str, help="the path where the area file is stored")
    parser.add_argument("info_directory", type=str, help="the directory where the poi index and poi category matrixes are stored")
    parser.add_argument("output_filepath", type=str, help="the path where save the array elaborated")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    info_dir = args.info_directory
    output_filepath = args.output_filepath

    main(input_filepath, info_dir, output_filepath)
