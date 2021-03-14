import os
import pandas as pd
import json
import numpy as np
import argparse
import sys
import scipy

def main():
    parser = argparse.ArgumentParser(description="Construct the w(r) matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("output_filepath", type=str, help="the file where store the index")
    args = parser.parse_args()
    input_dir = args.input_directory
    output_file = args.output_file

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    pattern_files = [path for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)

    safe_graph_place_ids = None
    for pattern_file in pattern_files:
        df = pd.read_csv(pattern_file)
        
        if safe_graph_place_ids == None:
            safe_graph_place_ids = df["safegraph_place_id"]
        else:
            safe_graph_place_ids.append(df["safegraph_place_id"])
    
    pois_idx = pd.unique(safe_graph_place_ids)
    matrix_positions = np.arange(0, len(pois_idx))

    result_poi_mapping = pd.DataFrame(data={'matrix_idx':matrix_positions,'poi_idx': pois_idx})

    result_poi_mapping.to_csv(output_filename)

        # row => POI (315'000)
        # column => CBG (12'000)
        # Around => 3'780'000'000 entries
        # Consequently => sparse matrix SciPy
        # Entry => 4 byte
        # Total => ~16GB
        


if __name__ == "__main__":
    main()