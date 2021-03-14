import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

def JSONParser(data):
    return json.loads(data)

def main():
    parser = argparse.ArgumentParser(description="Construct the w(r) matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the index result")
    args = parser.parse_args()
    input_dir = args.input_directory
    output_directory = args.output_directory

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    pattern_files = [os.path.join(input_dir, path) for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)

    safe_graph_place_ids_not_set = True
    cbgs = []
    for pattern_file in pattern_files:
        print("Reading CSV file", pattern_file)
        df = pd.read_csv(pattern_file, converters={"visitor_home_cbgs": JSONParser})
        
        if safe_graph_place_ids_not_set:
            safe_graph_place_ids = df["safegraph_place_id"]
            safe_graph_place_ids_not_set = False
        else:
            safe_graph_place_ids.append(df["safegraph_place_id"])
        
        for i, row in df.iterrows():
            cbgs.extend(row["visitor_home_cbgs"].keys())
    
    pois_idx = pd.unique(safe_graph_place_ids)
    matrix_positions = np.arange(0, len(pois_idx))
    result_poi_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "poi": pois_idx})
    result_poi_mapping.to_csv(os.path.join(output_directory, "poi_indexes.csv"), index=False)

    unique_cbgs = pd.unique(cbgs)
    matrix_positions = np.arange(0, len(unique_cbgs))
    result_cbg_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "cbg": unique_cbgs})
    result_cbg_mapping.to_csv(os.path.join(output_directory, "cbg_indexes.csv"), index=False)

if __name__ == "__main__":
    main()

# row => POI (315'000)
# column => CBG (12'000)
# Around => 3'780'000'000 entries
# Consequently => sparse matrix SciPy
# Entry => 4 byte
# Total => ~16GB

"{""360810040021"":7,""360810086001"":5,""360810020001"":5,""360850011003"":4,""360810178002"":4,""360810174001"":4,""360810942031"":4,""360810036002"":4,""360810098002"":4,""360810184022"":4,""360810062023"":4}"