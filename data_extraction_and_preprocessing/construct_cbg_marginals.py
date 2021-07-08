import argparse
import os
import sys

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, read_npy, read_npz

def main(input_dir, cbg_pop_matrix_directory, hci_dir, output_dir):
    poi_marg_files = get_dates_from_input_dir(input_dir, extension=".npz")
    cbg_pop_matrix_input = read_npy(os.path.join(cbg_pop_matrix_directory, "cbg_population_matrix.npy"))
    hci_files = get_dates_from_input_dir(hci_dir, extension=".npy")
    os.makedirs(output_dir, exist_ok=True)
    
    cbg_pop_matrix = np.reshape(cbg_pop_matrix_input, (cbg_pop_matrix_input.shape[0], 1))
    poi_marg_files.sort(key=lambda tup: tup[0])
    hci_files.sort(key=lambda tup: tup[0])

    for ((poi_marg_filename, poi_marg_filepath), (hci_filename, hci_filepath)) in zip(poi_marg_files, hci_files):
        poi_marg_matrix = read_npz(poi_marg_filepath)
        hci_matrix = read_npy(hci_filepath)

        n_pois_t = poi_marg_matrix.sum(axis=0)
        cbg_marginals = np.multiply(n_pois_t, np.repeat((hci_matrix * cbg_pop_matrix) / np.sum(hci_matrix * cbg_pop_matrix, axis=0), 24, axis=1))

        output_filepath = os.path.join(output_dir, os.path.splitext(poi_marg_filename)[0])
        print("Writing file", output_filepath)
        np.save(output_filepath, cbg_marginals)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg marginals using the poi marginals matrixes")
    parser.add_argument("input_directory", type=str, help="the directory where the poi marginals matrixes are stored")
    parser.add_argument("cbg_pop_matrix_directory", type=str, help="the directory where the cbg population matrix is stored")
    parser.add_argument("hci_directory", type=str, help="the directory where the hci matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    cbg_pop_matrix_directory = args.cbg_pop_matrix_directory
    hci_dir = args.hci_directory
    output_dir = args.output_directory
    
    main(input_dir, cbg_pop_matrix_directory, hci_dir, output_dir)
