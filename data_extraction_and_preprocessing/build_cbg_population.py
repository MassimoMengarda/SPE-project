import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, read_csv

def main(input_dir, index_dir, output_filepath):
    cbg_index_df = pd.read_csv(os.path.join(index_dir, "cbg_indexes.csv"))
    df = read_csv(os.path.join(input_dir, "cbg_b01.csv"))

    reduce_df = pd.DataFrame({'cbg':df['census_block_group'], 'cbg_population': df['B01003e1']})
    merged_df = pd.merge(cbg_index_df, reduce_df, on="cbg", how="left")
    merged_df["cbg_population"].fillna(0, inplace=True)

    print("Writing NPY", output_filepath)
    np.save(output_filepath, merged_df["cbg_population"])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg marginals using the v pj matrixes")
    parser.add_argument("input_directory", type=str, help="the path to where the cbg_b01 file is stored")
    parser.add_argument("index_directory", type=str, help="the directory where the cbg matrix is stored")
    parser.add_argument("output_filepath", type=str, help="the path where to save the result")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    output_filepath = args.output_filepath

    main(input_dir, index_dir, output_filepath)
