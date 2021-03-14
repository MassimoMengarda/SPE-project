import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import scipy

def JSONParser(data):
    j1 = json.loads(data)
    return j1

def main():
    parser = argparse.ArgumentParser(description="Construct the w(r) matrixes, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the weekly patterns are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    os.makedirs(output_dir)
    
    pattern_files = [path for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(pattern_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)


    for pattern_file in pattern_files:
        df = pd.read_csv(pattern_file, converters={'postal_code':str,'visitor_home_cbgs':JSONParser})
        sum_poi_cbg = [sum(df["visitor_home_cbgs"][i].values()) for x in df['col']]
        
        sum_poi_cbg = np.asarray(sum_poi_cbg)
        ratio = df["raw_visitor_counts"][i] / sum_poi_cbg

        data = []
        pois = []
        cbgs = []

        for idx, poi in df.iterrows():
            data.extend(poi["visitor_home_cbgs"].values() / sum_poi_cbg[idx] * ratio[idx])
            poi_idx.extend([idx for i in len(poi["visitor_home_cbgs"])])
            cbgs.extend(poi["visitor_home_cbgs"].keys())
        
        print(df)

if __name__ == "__main__":
    main()

# row => POI (315'000)
# column => CBG (12'000)
# Around => 3'780'000'000 entries
# Consequently => sparse matrix SciPy
# Entry => 4 byte
# Total => ~16GB