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
    parser.add_argument("delta_pj_matrixes_directory", type=str, help="the directory where the delta pj matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    delta_pj_dir = args.delta_pj_matrixes_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    poi_idx_filename = os.path.join(index_dir, "poi_indexes.csv")
    if not os.path.isfile(poi_idx_filename):
        print("The given indexes directory do not contain the valid index file")
        sys.exit(1)

    poi_idx_file = pd.read_csv(poi_idx_filename)

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isdir(delta_pj_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    pattern_files = [(path, os.path.join(input_dir, path)) for path in os.listdir(input_dir) if path.endswith(".csv")]
    delta_pj_files = [os.path.join(delta_pj_dir, path) for path in os.listdir(delta_pj_dir) if path.endswith(".npy")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)
        
    if len(delta_pj_files) == 0:
        print("Given input directory do not contain any NPY file") 
        sys.exit(1)

    for (filename, pattern_file), delta_pj_filename in zip(pattern_files, delta_pj_files):
        print("Reading CSV file", pattern_file)
        df = pd.read_csv(pattern_file, converters={"postal_code": str, "visits_by_each_hour": JSONParser})

        reduced_df = pd.DataFrame(data={"poi": df["safegraph_place_id"], "visits_by_each_hour": df["visits_by_each_hour"]})
        merged_df = pd.merge(poi_idx_file, reduced_df, on="poi", how="left")

        zero_hour_list = [0 for i in range(168)] # 24 x 7
        for row in merged_df.loc[merged_df["visits_by_each_hour"].isnull(), "visits_by_each_hour"].index:
            merged_df.at[row, "visits_by_each_hour"] = zero_hour_list
        
        # print(merged_df["visits_by_each_hour"])
        v_pj_t_matrix = merged_df["visits_by_each_hour"].tolist()
        v_pj_t_matrix = np.asarray(v_pj_t_matrix, dtype=np.uint16)
        visitor_in_the_place_matrix = np.zeros(v_pj_t_matrix.shape)

        print("Reading NPY file", delta_pj_filename)
        delta_pj_matrix = np.load(delta_pj_filename)
        delta_pj_matrix = np.reshape(delta_pj_matrix, (delta_pj_matrix.shape[0], 1))
        dwell = np.ceil(delta_pj_matrix)

        print("v_pj_t_matrix")
        print(v_pj_t_matrix)

        print("v_pj_t_matrix.shape")
        print(v_pj_t_matrix.shape)

        print("dwell")
        print(dwell)

        for i in range(v_pj_t_matrix.shape[1]):
            hour_visitor_to_report_from_i = np.reshape(v_pj_t_matrix[:, i].copy(), (v_pj_t_matrix.shape[0], 1))
            print("hour_visitor_to_report_from_i")
            print(hour_visitor_to_report_from_i)

            for j in range(i, v_pj_t_matrix.shape[1]):
                visitor_to_be_resetted = (dwell < j - i).flatten()
                print("visitor_to_be_resetted")
                print(visitor_to_be_resetted)
                hour_visitor_to_report_from_i[visitor_to_be_resetted, :] = 0

                print("hour_visitor_to_report_from_i")
                print(hour_visitor_to_report_from_i)

                print("hour_visitor_to_report_from_i.shape")
                print(hour_visitor_to_report_from_i.shape)

                print("visitor_in_the_place_matrix.shape")
                print(visitor_in_the_place_matrix.shape)

                sum_visitor = visitor_in_the_place_matrix[:, j] + hour_visitor_to_report_from_i                
                
                print("sum_visitor")
                print(sum_visitor)
                print("sum_visitor.shape")
                print(sum_visitor.shape)

                #visitor_in_the_place_matrix[:, j] = 
        
        print("visitor_in_the_place_matrix")
        print(visitor_in_the_place_matrix)
        
        visitor_in_the_place_sparse_matrix = coo_matrix(visitor_in_the_place_matrix)
        output_filepath = os.path.join(output_dir, (os.path.splitext(filename)[0] + ".npz"))
        print("Writing file", output_filepath)
        save_npz(output_filepath, visitor_in_the_place_sparse_matrix)

if __name__ == "__main__":
    main()
    