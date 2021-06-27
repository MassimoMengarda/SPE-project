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
    
    is_aggregate_sum_w_set = False
    aggregate_sum_w = None
    
    for _, pattern_file in pattern_files:
        df = read_csv(pattern_file, converters={"postal_code": str, "visitor_home_cbgs": JSONParser})
        
        print("Computing ratio")
        sum_poi_cbg = [sum(x.values()) for x in df["visitor_home_cbgs"]]
        
        sum_poi_cbg = np.asarray(sum_poi_cbg)
        ratio = df["raw_visitor_counts"] / sum_poi_cbg

        data = []
        pois = []
        cbgs = []
        print("Computing weights")
        for idx, poi in df.iterrows():
            data.extend(list(poi["visitor_home_cbgs"].values()) / sum_poi_cbg[idx] * ratio[idx])
            pois.extend([poi["safegraph_place_id"] for i in range(len(poi["visitor_home_cbgs"]))])
            cbgs.extend(poi["visitor_home_cbgs"].keys())
        
        print("Computing POI indexes")
        weights_df = pd.DataFrame(data={"data": data, "poi": pois, "cbg": cbgs})
        result_poi_merge = pd.merge(weights_df, poi_idx_file, on="poi")

        print("Computing CBG indexes")
        result_merge = pd.merge(result_poi_merge, cbg_idx_file, on="cbg")

        coo_init_value = (result_merge["data"], (result_merge["poi_matrix_idx"], result_merge["cbg_matrix_idx"]))
        coo_shape = (poi_idx_file["poi_matrix_idx"].max() + 1, cbg_idx_file["cbg_matrix_idx"].max() + 1)
        
        w_r_sparse_matrix = coo_matrix(coo_init_value, shape=coo_shape)

        if is_aggregate_sum_w_set:
            aggregate_sum_w += w_r_sparse_matrix
        else:
            aggregate_sum_w = w_r_sparse_matrix
            is_aggregate_sum_w_set = True

        # No need to save these files
        # output_filepath = os.path.join(output_dir, (os.path.splitext(filename)[0] + ".npz"))
        # print("Writing file", output_filepath)
        # save_npz(output_filepath, w_r_sparse_matrix)

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
