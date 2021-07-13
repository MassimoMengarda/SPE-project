import argparse
import os

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, JSONParser, read_csv

def main(input_directory, zip_cbg_filepath, info_directory):
    pattern_files = get_dates_from_input_dir(input_directory)
    os.makedirs(info_directory, exist_ok=True)

    is_safe_graph_place_ids_set = False
    cbgs = []
    for _, pattern_file in pattern_files:
        df = read_csv(pattern_file, converters={"visitor_home_cbgs": JSONParser})
        
        if is_safe_graph_place_ids_set:
            safe_graph_place_ids.append(df["safegraph_place_id"])
        else:
            safe_graph_place_ids = df["safegraph_place_id"]
            is_safe_graph_place_ids_set = True
        
        for _, row in df.iterrows():
            cbgs.extend(row["visitor_home_cbgs"].keys())
    
    pois_idx = pd.unique(safe_graph_place_ids)
    matrix_positions = np.arange(0, len(pois_idx))
    result_poi_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "poi": pois_idx})

    info_filepath = os.path.join(info_directory, "poi_indexes.csv")
    print("Writing csv file", info_filepath)
    result_poi_mapping.to_csv(info_filepath, index=False)

    zip_cbg_bind_df = read_csv(zip_cbg_filepath, converters={'cbg': str, 'zip': str})
    unique_cbgs = pd.unique(zip_cbg_bind_df["cbg"])
    matrix_positions = np.arange(0, len(unique_cbgs))
    result_cbg_mapping = pd.DataFrame(data={"matrix_idx": matrix_positions, "cbg": unique_cbgs})

    output_filepath = os.path.join(info_directory, "cbg_indexes.csv")
    print("Writing csv file", output_filepath)
    result_cbg_mapping.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the poi cbg index matrixes")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("zip_cbg_filepath", type=str, help="the directory where the bind between CBG and ZIP list")
    parser.add_argument("info_directory", type=str, help="the directory where store the index result")
    
    args = parser.parse_args()
    input_directory = args.input_directory
    zip_cbg_filepath = args.zip_cbg_filepath
    info_directory = args.info_directory

    main(input_directory, zip_cbg_filepath, info_directory)
