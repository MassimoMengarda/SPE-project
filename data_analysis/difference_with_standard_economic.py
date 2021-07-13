import argparse
import os
from matplotlib.colors import Normalize

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_extraction_and_preprocessing.utils import read_npy, read_csv

plt.style.use("seaborn-whitegrid")


def main(countermeasure_results_dir, naics_to_io_filepath, output_dir):
    economic_results_countermeasure = read_npy(os.path.join(countermeasure_results_dir, "sector_graph.npy"))
    print("economic_results_countermeasure.shape", economic_results_countermeasure.shape)

    io_sectors_df = read_csv(naics_to_io_filepath, sep=";", index_col="sector_number")

    loss_percentage = (economic_results_countermeasure[1] - economic_results_countermeasure[2]) / economic_results_countermeasure[1]
    loss_df = pd.DataFrame({"loss_percentage": loss_percentage}, index=economic_results_countermeasure[0])
    
    merged_dataset = loss_df.merge(io_sectors_df, left_index=True, right_index=True)
    merged_dataset.sort_values("loss_percentage", inplace=True, ascending=False)
    merged_dataset = merged_dataset[:10]
    
    ax = merged_dataset.plot.barh(x="name", y="loss_percentage", xlim=(0, 1)) #labels=merged_dataset["name"]
    # plt.xticks([i for i in range(10)], merged_dataset["name"], rotation=45)
    # plt.xticks(merged_dataset.index[:10], merged_dataset["name"], rotation=45)
    plt.xticks(rotation=45, rotation_mode='anchor')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute the difference between a standard case and a case with some counter measure applied to them")
    parser.add_argument("countermeasure_results_dir", type=str, help="the directory where the counter-measures simulation results are stored")
    parser.add_argument("naics_to_io_filepath", type=str, help="the path where the naics to io sector file is stored")
    parser.add_argument("output_dir", type=str, help="the directory where store the result")

    args = parser.parse_args()
    countermeasure_results_dir = args.countermeasure_results_dir
    naics_to_io_filepath = args.naics_to_io_filepath
    output_dir = args.output_dir
    
    main(countermeasure_results_dir, naics_to_io_filepath, output_dir)