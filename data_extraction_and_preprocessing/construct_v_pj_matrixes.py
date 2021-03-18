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
    parser = argparse.ArgumentParser(description="Construct the v_pj(t) matrixes, one for each week considered")
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

    if not os.path.isfile(poi_idx_filename):
        print("The given indexes directory do not contain the valid index file")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)

    poi_idx_file = pd.read_csv(poi_idx_filename)
    
    pattern_files = [(path, os.path.join(input_dir, path)) for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)

    for filename, pattern_file in pattern_files:
        print("Reading CSV file ", pattern_file)
        df = pd.read_csv(pattern_file, converters={"postal_code": str, "visits_by_each_hour": JSONParser})

        reduced_df = pd.DataFrame(data={"poi": df["safegraph_place_id"], "visits_by_each_hour": df["visits_by_each_hour"]})
        merged_df = pd.merge(poi_idx_file, reduced_df, on="poi", how="left")

        zero_hour_list = [0 for i in range(168)] # 24 x 7
        for row in merged_df.loc[merged_df["visits_by_each_hour"].isnull(), "visits_by_each_hour"].index:
            merged_df.at[row, "visits_by_each_hour"] = zero_hour_list
        
        # print(merged_df["visits_by_each_hour"])
        v_pj_t_matrix = merged_df["visits_by_each_hour"].tolist()
        v_pj_t_matrix = np.asarray(v_pj_t_matrix, dtype=np.uint16)
        
        v_pj_t_sparse_matrix = coo_matrix(v_pj_t_matrix)
        output_filepath = os.path.join(output_dir, (os.path.splitext(filename)[0] + ".npz"))
        print("Writing file", output_filepath)
        save_npz(output_filepath, v_pj_t_sparse_matrix)

if __name__ == "__main__":
    main()
    