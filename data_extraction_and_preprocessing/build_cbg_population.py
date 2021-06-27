import argparse
import os

import numpy as np
import pandas as pd

from utils import read_csv

def main(input_filepath, info_dir):
    cbg_index_df = read_csv(os.path.join(info_dir, "cbg_indexes.csv"))
    df = read_csv(input_filepath)

    reduce_df = pd.DataFrame({'cbg':df['census_block_group'], 'cbg_population': df['B01003e1']})
    merged_df = pd.merge(cbg_index_df, reduce_df, on="cbg", how="left")
    merged_df.loc[merged_df["cbg_population"] == 0, "cbg_population"] = 1
    merged_df["cbg_population"].fillna(1, inplace=True) # fill with 1 to avoid problems with divisions

    output_filepath = os.path.join(info_dir, "cbg_population_matrix.npy")
    print("Writing NPY", output_filepath)
    np.save(output_filepath, merged_df["cbg_population"].to_numpy().astype(np.int32))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg population matrix")
    parser.add_argument("input_filepath", type=str, help="the path to the cbg_b01.csv file")
    parser.add_argument("info_directory", type=str, help="the directory where the cbg id matrix is stored")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    info_dir = args.info_directory

    main(input_filepath, info_dir)
