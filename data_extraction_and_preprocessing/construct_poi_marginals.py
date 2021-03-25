import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz

from utils import JSONParser, get_dates_from_input_dir, read_csv, read_npy

def main(input_dir, index_dir, delta_pj_dir, output_dir):    
    poi_idx_file = read_csv(os.path.join(index_dir, "poi_indexes.csv"))
    poi_categories_df = read_csv(os.path.join(index_dir, "poi_categories.csv"))
    pattern_files = get_dates_from_input_dir(input_dir)
    delta_pj_files = get_dates_from_input_dir(delta_pj_dir, extension=".npy")
    os.makedirs(output_dir, exist_ok=True)

    categories = pd.unique(poi_categories_df["top_category"])
    categories = categories[~pd.isnull(categories)]

    for (filename, pattern_file), delta_pj_filename in zip(pattern_files, delta_pj_files):
        df = read_csv(pattern_file, converters={"postal_code": str, "visits_by_each_hour": JSONParser})

        reduced_df = pd.DataFrame(data={"poi": df["safegraph_place_id"], "visits_by_each_hour": df["visits_by_each_hour"]})
        merged_df = pd.merge(poi_idx_file, reduced_df, on="poi", how="left")

        zero_hour_list = [0 for i in range(168)] # 24 x 7
        for row in merged_df.loc[merged_df["visits_by_each_hour"].isnull(), "visits_by_each_hour"].index:
            merged_df.at[row, "visits_by_each_hour"] = zero_hour_list
        
        v_pj_t_matrix = merged_df["visits_by_each_hour"].tolist()
        v_pj_t_matrix = np.asarray(v_pj_t_matrix, dtype=np.float32)
        visitor_in_the_place_matrix = np.zeros(v_pj_t_matrix.shape)

        delta_pj_matrix = read_npy(delta_pj_filename)
        
        dwell_correction_factor = delta_pj_matrix.copy()
        dwell = np.ceil(delta_pj_matrix)
        dwell_correction_factor = dwell_correction_factor / dwell

        print("Computing visitors at each hour")
        for i in range(v_pj_t_matrix.shape[1]):
            hour_visitor_to_report_from_i = v_pj_t_matrix[:, [i]]

            for j in range(i, v_pj_t_matrix.shape[1]):
                visitor_to_be_resetted = (dwell < j - i)
                hour_visitor_to_report_from_i[visitor_to_be_resetted, :] = 0

                sum_visitor = visitor_in_the_place_matrix[:, [j]] + hour_visitor_to_report_from_i
                visitor_in_the_place_matrix[:, [j]] = sum_visitor
        
        visitor_in_the_place_matrix = visitor_in_the_place_matrix * np.reshape(dwell_correction_factor, (dwell_correction_factor.shape[0], 1))
        
        # Each outlier is set to the 95th percentile
        print("Computing outliers")
        for category in categories:
            this_category = poi_categories_df["top_category"] == category
            quantile_95th = np.quantile(visitor_in_the_place_matrix[this_category], 0.95, axis=0)

            category_column = np.reshape(this_category.values, (this_category.shape[0], 1))
            is_in_category_matrix = np.repeat(category_column, visitor_in_the_place_matrix.shape[1], axis=1)

            visitor_to_modify = np.logical_and(is_in_category_matrix, visitor_in_the_place_matrix > quantile_95th)
            np.putmask(visitor_in_the_place_matrix, visitor_to_modify, np.reshape(quantile_95th, (1, quantile_95th.shape[0])))
            
        visitor_in_the_place_sparse_matrix = coo_matrix(visitor_in_the_place_matrix)

        us_population = 322087547
        safegraph_devices = 47971302
        visitor_in_the_place_sparse_matrix *= (us_population / safegraph_devices)
        
        output_filepath = os.path.join(output_dir, (os.path.splitext(filename)[0] + ".npz"))
        print("Writing file", output_filepath)
        save_npz(output_filepath, visitor_in_the_place_sparse_matrix)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the poi marginal matrixes, one for each weekly pattern considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("index_directory", type=str, help="the directory where the poi index matrix is stored")
    parser.add_argument("delta_pj_matrixes_directory", type=str, help="the directory where the delta pj matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    delta_pj_dir = args.delta_pj_matrixes_directory
    output_dir = args.output_directory

    main(input_dir, index_dir, delta_pj_dir, output_dir)
