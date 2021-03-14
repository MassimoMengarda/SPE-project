import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz

def JSONParser(data):
    j1 = json.loads(data)
    return j1

def main():
    parser = argparse.ArgumentParser(description="Construct the w(r) matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("index_directory", type=str, help="the directory where the matrix index are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    poi_idx_filename = os.path.join(index_dir, "poi_indexes.csv")
    cbg_idx_filename = os.path.join(index_dir, "cbg_indexes.csv")

    if (not os.path.isfile(poi_idx_filename)) or (not os.path.isfile(cbg_idx_filename)):
        print("The given indexes directory do not contain the valid index files")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)

    poi_idx_file = pd.read_csv(poi_idx_filename)
    poi_idx_file.rename(columns={"matrix_idx": "poi_matrix_idx"}, inplace=True)
    cbg_idx_file = pd.read_csv(cbg_idx_filename, converters={"cbg": str})
    cbg_idx_file.rename(columns={"matrix_idx": "cbg_matrix_idx"}, inplace=True)
    
    pattern_files = [(path, os.path.join(input_dir, path)) for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)

    for filename, pattern_file in pattern_files:
        print("Reading CSV file ", pattern_file)
        df = pd.read_csv(pattern_file, converters={"postal_code": str, "visitor_home_cbgs": JSONParser})
        
        print("Computing ratio")
        sum_poi_cbg = [sum(x.values()) for x in df["visitor_home_cbgs"]]
        
        sum_poi_cbg = np.asarray(sum_poi_cbg)
        ratio = df["raw_visitor_counts"] / sum_poi_cbg

        print("Computing weights")

        data = []
        pois = []
        cbgs = []

        for idx, poi in df.iterrows():
            data.extend(list(poi["visitor_home_cbgs"].values()) / sum_poi_cbg[idx] * ratio[idx])
            pois.extend([poi["safegraph_place_id"] for i in range(len(poi["visitor_home_cbgs"]))])
            cbgs.extend(poi["visitor_home_cbgs"].keys())
        
        print("Computing POI indexes")

        weights_df = pd.DataFrame(data={'data': data, 'poi': pois, 'cbg': cbgs})
        result_poi_merge = pd.merge(weights_df, poi_idx_file, on="poi")

        print("Computing CBG indexes")
        result_merge = pd.merge(result_poi_merge, cbg_idx_file, on="cbg")
        
        # print(result_merge)

        
        # poi_idxs = pois_series.apply(lambda poi: poi_idx_file['matrix_idx'][poi_idx_file['poi'] == poi].values[0])
        
        # poi_idxs = []
        # for poi in pois:
        #     poi_idxs.append(poi_idx_file.loc[poi_idx_file["poi"] == poi].iloc[0]["matrix_idx"])
        # print(poi_idxs)

        # print("Computing CBG indexes")
# 
        # cbg_idxs = []
        # for cbg in cbgs:
        #     cbg_idxs.append(cbg_idx_file.loc[cbg_idx_file["cbg"] == cbg].iloc[0]["matrix_idx"])
        
        # print("Creating sparse matrix")

        coo_init_value = (result_merge['data'], (result_merge['poi_matrix_idx'], result_merge['cbg_matrix_idx']))
        coo_shape = (poi_idx_file['poi_matrix_idx'].max() + 1, cbg_idx_file['cbg_matrix_idx'].max() + 1)
        
        # print((result_merge['poi_matrix_idx'] >= coo_shape[0]).sum())
        # print((result_merge['poi_matrix_idx'] > coo_shape[0]).sum())
        # print(result_merge['poi_matrix_idx'].isnull().sum())
        # print((result_merge['cbg_matrix_idx'] >= coo_shape[1]).sum())
        # print((result_merge['cbg_matrix_idx'] > coo_shape[1]).sum())
        # print(result_merge['cbg_matrix_idx'].isnull().sum())
# 
        # print(coo_shape)
        
        w_r_sparse_matrix = coo_matrix(coo_init_value, shape=coo_shape)
        output_filepath = os.path.join(output_dir, (os.path.splitext(filename)[0] + ".npz"))
        print("Writing file ", output_filepath)
        save_npz(output_filepath, w_r_sparse_matrix)



if __name__ == "__main__":
    main()

# row => POI (315'000)
# column => CBG (12'000)
# Around => 3'780'000'000 entries
# Consequently => sparse matrix SciPy
# Entry => 4 byte
# Total => ~16GB
