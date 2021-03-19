import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, JSONParser

def main():
    parser = argparse.ArgumentParser(description="Construct the poi cbg index matrixes")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the index result")
    args = parser.parse_args()
    input_dir = args.input_directory
    output_directory = args.output_directory

    if not os.path.isdir(input_dir):
        sys.exit("Input directory is not a directory")
    
    pattern_files = get_dates_from_input_dir(input_dir)

    if len(pattern_files) == 0:
        sys.exit("Given input directory do not contain any CSV file")

    os.makedirs(output_directory, exist_ok=True)

    is_safe_graph_place_ids_set = False
    cbgs = []
    for pattern_file in pattern_files:
        print("Reading CSV file", pattern_file)
        df = pd.read_csv(pattern_file, converters={"visitor_home_cbgs": JSONParser})
        
        if is_safe_graph_place_ids_set:
            safe_graph_place_ids.append(df["safegraph_place_id"])
        else:
            safe_graph_place_ids = df["safegraph_place_id"]
            is_safe_graph_place_ids_set = True
        
        for i, row in df.iterrows():
            cbgs.extend(row["visitor_home_cbgs"].keys())
    
    pois_idx = pd.unique(safe_graph_place_ids)
    matrix_positions = np.arange(0, len(pois_idx))
    result_poi_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "poi": pois_idx})

    output_filepath = os.path.join(output_directory, "poi_indexes.csv")
    print("Writing csv file", output_filepath)
    result_poi_mapping.to_csv(output_filepath, index=False)

    unique_cbgs = pd.unique(cbgs)
    matrix_positions = np.arange(0, len(unique_cbgs))
    result_cbg_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "cbg": unique_cbgs})

    output_filepath = os.path.join(output_directory, "cbg_indexes.csv")
    print("Writing csv file", output_filepath)
    result_cbg_mapping.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    main()

# row => POI (315'000)
# column => CBG (12'000)
# Around => 3'780'000'000 entries
# Consequently => sparse matrix SciPy
# Entry => 4 byte
# Total => ~16GB

"{""360810040021"":7,""360810086001"":5,""360810020001"":5,""360850011003"":4,""360810178002"":4,""360810174001"":4,""360810942031"":4,""360810036002"":4,""360810098002"":4,""360810184022"":4,""360810062023"":4}"