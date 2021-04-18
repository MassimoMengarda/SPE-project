
import argparse
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, find, save_npz

from utils import (JSONParser, get_dates_from_input_dir, read_csv, read_npy,
                   read_npz)

from joblib import Parallel, delayed

def ipfp_hour(aggregate_visits_w, cbg_marginals_u, poi_marginal_v, number_of_iterations=100):
    last_w = aggregate_visits_w
    
    for tau in range(1, number_of_iterations):
        new_w = None
        if tau % 2 == 1: # if tau is odd
            last_w_axis_sum = last_w.sum(axis=0)
            last_w_axis_sum[last_w_axis_sum < sys.float_info.epsilon] = 1.0
            alfa_i = cbg_marginals_u / last_w_axis_sum
            new_w = last_w.multiply(alfa_i)                
        else:
            last_w_axis_sum = last_w.sum(axis=1)
            last_w_axis_sum[last_w_axis_sum < sys.float_info.epsilon] = 1.0
            last_w_coo = coo_matrix(last_w_axis_sum)
            alfa_j = poi_marginal_v / last_w_coo
            new_w = last_w.multiply(alfa_j)
        last_w = new_w
    return last_w

def ipfp(day, hour, aggregate_visits_w, cbg_marginals_u, poi_marginal_v, day_dir):
    print(f"Computing IPFP {day} - hour {hour}")
    w_sparse_matrix = ipfp_hour(aggregate_visits_w, cbg_marginals_u, poi_marginal_v, number_of_iterations=100)
    w_matrix_filename = os.path.join(day_dir, "{:0>3d}.npz".format(hour))
    print("Saving NPZ", w_matrix_filename)
    save_npz(w_matrix_filename, w_sparse_matrix)

def main(aggregate_visit_matrix_dir, cbg_marginals_dir, poi_marginals_dir, output_dir, no_weeks=None):    
    aggregate_visits_w = read_npz(os.path.join(aggregate_visit_matrix_dir, "aggregate_visit_matrix.npz"))
    cbg_marginals_files = get_dates_from_input_dir(cbg_marginals_dir, extension=".npy")
    poi_marginals_files = get_dates_from_input_dir(poi_marginals_dir, extension=".npz")
    os.makedirs(output_dir, exist_ok=True)

    cbg_marginals_files.sort(key=lambda tup: tup[0])
    poi_marginals_files.sort(key=lambda tup: tup[0])

    for (filename, cbg_marginal_filepath), (_, poi_marginal_filepath) in zip(cbg_marginals_files, poi_marginals_files):
        day = datetime.strptime(filename[:len("2019-01-08")], "%Y-%m-%d").strftime("%Y-%m-%d")
        if not no_weeks is None and day in no_weeks:
            print(f"Skipping {day}")
            continue

        day_dir = os.path.join(output_dir, day)
        os.makedirs(day_dir, exist_ok=True)
        cbg_marginals_u_t = read_npy(cbg_marginal_filepath)
        poi_marginal_v_t = read_npz(poi_marginal_filepath)
        
        Parallel(n_jobs=4)(
            (delayed(ipfp)(day, hour, aggregate_visits_w, cbg_marginals_u_t[:, hour], poi_marginal_v_t.getcol(hour), day_dir) for hour in range(cbg_marginals_u_t.shape[1]))
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the v_pj(t) matrixes, one for each week considered")
    parser.add_argument("aggregate_visit_matrix_directory", type=str, help="the directory where the aggregate visit matrix is stored")
    parser.add_argument("cbg_marginals_directory", type=str, help="the directory where the cbg marginals are stored")
    parser.add_argument("poi_marginals_directory", type=str, help="the directory where the poi marginals are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the results")
    parser.add_argument("-nw", "--no_weeks", nargs="*", help="specify the weeks you want to exclude", default=None)
    args = parser.parse_args()
    aggregate_visit_matrix_dir = args.aggregate_visit_matrix_directory
    cbg_marginals_dir = args.cbg_marginals_directory
    poi_marginals_dir = args.poi_marginals_directory
    output_dir = args.output_directory
    no_weeks = args.no_weeks

    main(aggregate_visit_matrix_dir, cbg_marginals_dir, poi_marginals_dir, output_dir, no_weeks)
