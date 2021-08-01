import argparse
import os

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz

from utils import JSONParser, get_dates_from_input_dir, read_csv

def main(input_dir, info_dir, output_dir):
    poi_idx_file = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    cbg_idx_file = read_csv(os.path.join(info_dir, "cbg_indexes.csv"), converters={"cbg": str})
    pattern_files = get_dates_from_input_dir(input_dir)
    os.makedirs(output_dir, exist_ok=True)

    poi_idx_file.rename(columns={"matrix_idx": "poi_matrix_idx"}, inplace=True)
    cbg_idx_file.rename(columns={"matrix_idx": "cbg_matrix_idx"}, inplace=True)
        
    coo_shape = (poi_idx_file["poi_matrix_idx"].max() + 1, cbg_idx_file["cbg_matrix_idx"].max() + 1)

    visitors_data = []
    cbgs_ids = []
    pois_ids = []
    
    for _, pattern_file in pattern_files:
        df = read_csv(pattern_file, converters={"postal_code": str, "visitor_home_cbgs": JSONParser})
        
        for _, poi in df.iterrows():
            cbgs_ids.extend(poi["visitor_home_cbgs"].keys())
            visitors_data.extend(poi["visitor_home_cbgs"].values())
            pois_ids.extend([poi["safegraph_place_id"] for i in range(len(poi["visitor_home_cbgs"]))])
    
    df = pd.DataFrame({'cbg': cbgs_ids, 'poi': pois_ids, 'visitors': visitors_data})
    result_poi_merge = pd.merge(df, poi_idx_file, on="poi")
    result_merge = pd.merge(result_poi_merge, cbg_idx_file, on="cbg")
    result_merge.drop(columns=['cbg','poi'])

    merged_dataframe = result_merge.groupby(['poi_matrix_idx', 'cbg_matrix_idx']).sum()
    merged_dataframe.reset_index(level=['poi_matrix_idx', 'cbg_matrix_idx'], inplace=True)

    coo_value = (merged_dataframe["visitors"].to_numpy(dtype=np.float64), (merged_dataframe["poi_matrix_idx"], merged_dataframe["cbg_matrix_idx"]))
    aggregate_sum_w = coo_matrix(coo_value, shape=coo_shape)

    R = len(pattern_files) # Number of weeks to be considered
    aggregate_sum_w /= R

    output_filepath = os.path.join(output_dir, "aggregate_visit_matrix.npz")
    print("Writing file", output_filepath)
    save_npz(output_filepath, aggregate_sum_w)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the w(r) matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the poi and cbg index matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    info_dir = args.info_directory
    output_dir = args.output_directory

    main(input_dir, info_dir, output_dir)
