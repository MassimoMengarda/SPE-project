import argparse
import json
import os
import sys

from ..utils import read_csv

def main(io_matrix_dir, scale_factor_filepath, output_dir):
    print("Reading file", scale_factor_filepath)
    with open(scale_factor_filepath, 'r') as fhandle:
        scale_factor = json.load(fhandle)["metro_area_scale_factor"]
    
    if not os.path.isdir(io_matrix_dir):
        sys.exit(io_matrix_dir + " is not a valid directory")

    os.makedirs(output_dir, exist_ok=True)
    
    for io_matrix in os.listdir(io_matrix_dir):
        io_matrix_path = os.path.join(io_matrix_dir, io_matrix)
        io_matrix_df = read_csv(io_matrix_path, index_col="Sector")
        io_matrix_df_scaled = io_matrix_df * scale_factor

        scaled_output_filepath = os.path.join(output_dir, io_matrix)

        print("Writing file ", scaled_output_filepath)
        io_matrix_df_scaled.to_csv(scaled_output_filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the IO matrixes strating from POI categories and NAICS codes")
    parser.add_argument("io_matrix_dir", type=str, help="the directory containing the economics IO matrixes")
    parser.add_argument("scale_factor_filepath", type=str, help="the path to the file containing the scale factor of the IO matrix")
    parser.add_argument("output_dir", type=str, help="the directory where to save the results")
    
    args = parser.parse_args()
    io_matrix_dir = args.io_matrix_dir
    scale_factor_filepath = args.scale_factor_filepath
    output_dir = args.output_dir
    main(io_matrix_dir, scale_factor_filepath, output_dir)
