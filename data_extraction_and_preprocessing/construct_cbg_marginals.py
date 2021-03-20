import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz, load_npz

from utils import get_dates_from_input_dir

def main():
    parser = argparse.ArgumentParser(description="Construct the cbg marginals using the v pj matrixes")
    parser.add_argument("input_directory", type=str, help="the directory where the v pj matrixes are stored")
    parser.add_argument("cbg_pop_matrix_directory", type=str, help="the directory where the cbg population matrix is stored")
    parser.add_argument("hci_directory", type=str, help="the directory where the hci matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where to save the results")
    args = parser.parse_args()
    input_dir = args.input_directory
    cbg_pop_matrix_directory = args.cbg_pop_matrix_directory
    hci_dir = args.hci_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        sys.exit("Input directory is not a directory")

    vpj_files = get_dates_from_input_dir(input_dir, extension=".npz")

    if len(vpj_files) == 0:
        sys.exit("Given input directory do not contain any NPZ file")

    cbg_pop_matrix_filepath = os.path.join(cbg_pop_matrix_directory, "cbg_population_matrix.npy")
    
    if not os.path.isfile(cbg_pop_matrix_filepath):
        sys.exit("The cbg population input directory is not valid")

    cbg_pop_matrix_input = np.load(cbg_pop_matrix_filepath)
    cbg_pop_matrix = np.reshape(cbg_pop_matrix_input, (cbg_pop_matrix_input.shape[0], 1))

    if not os.path.isdir(hci_dir):
        sys.exit("Input directory is not a directory")

    hci_files = get_dates_from_input_dir(hci_dir, extension=".npy")

    if len(hci_files) == 0:
        sys.exit("Given input directory do not contain any NPY file")
    
    vpj_files.sort(key=lambda tup: tup[0])
    hci_files.sort(key=lambda tup: tup[0])

    os.makedirs(output_dir, exist_ok=True)

    for ((vpj_filename, vpj_filepath), (hci_filename, hci_filepath)) in zip(vpj_files, hci_files):
        print("Reading NPZ file", vpj_filepath)
        vpj_matrix = load_npz(vpj_filepath)

        print("Reading NPY file", hci_filepath)
        hci_matrix = np.load(hci_filepath)

        n_pois_t = vpj_matrix.sum(axis=0)
        cbg_marginals = np.multiply(n_pois_t, np.repeat((hci_matrix * cbg_pop_matrix) / np.sum(hci_matrix * cbg_pop_matrix, axis=0), 24, axis=1))

        output_filepath = os.path.join(output_dir, vpj_filename)
        print("Writing file", output_filepath)
        np.save(output_filepath, cbg_marginals)

if __name__ == "__main__":
    main()