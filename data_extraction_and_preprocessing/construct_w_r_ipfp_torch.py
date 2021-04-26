
import argparse
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, find, save_npz

from utils import JSONParser, get_dates_from_input_dir, read_csv, read_npy, read_npz
from utils_torch import coo_to_tensor_torch

from joblib import Parallel, delayed

import joblib
import time

import torch

def sparse_dense_mul(s, d):
  i = s.indices()
  v = s.values()
  dv = d[i[0,:], i[1,:]]  # get values from relevant entries of dense matrix
  return torch.sparse_coo_tensor(i, v * dv, s.size()).coalesce()

def coo_get_col_to_dense(coo, col_index):
    mask = coo.indices()[1, :] == col_index
    col_indexes = coo.indices()[:, mask]
    col_indexes[1, :] -= col_index
    return torch.sparse_coo_tensor(col_indexes, coo.values()[mask], size=(coo.shape[0], 1)).to_dense()

def coo_scipy_to_coo_torch(coo):
    indices = np.vstack((coo.row, coo.col))

    return torch.sparse_coo_tensor(torch.from_numpy(indices), torch.from_numpy(coo.data), size=coo.shape).coalesce()

def copy_sparse_matrix(coo):
    return torch.clone(coo)

def ipfp_hour(aggregate_visits_w, cbg_marginals_u, poi_marginal_v, number_of_iterations=100):
    last_w = copy_sparse_matrix(aggregate_visits_w)
    
    for tau in range(1, number_of_iterations):
        new_w = None
        if tau % 2 == 1: # if tau is odd
            last_w_axis_sum = torch.sparse.sum(last_w, dim=0).to_dense()
            last_w_axis_sum[last_w_axis_sum < sys.float_info.epsilon] = 1.0
            alfa_i = cbg_marginals_u / last_w_axis_sum
            alfa_i = torch.reshape(alfa_i, (1, alfa_i.shape[0]))
            new_w = sparse_dense_mul(last_w, torch.broadcast_to(alfa_i, last_w.shape))
        else:
            last_w_axis_sum = torch.sparse.sum(last_w, dim=1).to_dense()
            last_w_axis_sum[last_w_axis_sum < sys.float_info.epsilon] = 1.0
            last_w_axis_sum = torch.reshape(last_w_axis_sum, (last_w_axis_sum.shape[0], 1))
            alfa_j = poi_marginal_v / last_w_axis_sum
            new_w = sparse_dense_mul(last_w, torch.broadcast_to(alfa_j, last_w.shape))
        last_w = new_w
    return last_w

def ipfp(day, hour, aggregate_visits_w, cbg_marginals_u, poi_marginal_v, day_dir):
    print(f"Computing IPFP {day} - hour {hour}")
    start_time = time.time()
    w_sparse_matrix = ipfp_hour(aggregate_visits_w, cbg_marginals_u, poi_marginal_v, number_of_iterations=100)
    print("Hour compute time: %s" % (time.time() - start_time))
    w_matrix_filename = os.path.join(day_dir, "{:0>3d}.pth".format(hour))
    print("Saving torch COO ", w_matrix_filename)
    torch.save(w_sparse_matrix, w_matrix_filename)

def main(aggregate_visit_matrix_dir, cbg_marginals_dir, poi_marginals_dir, output_dir, no_weeks=None):    
    if not torch.cuda.is_available():
        print("This program require a CUDA accelerator available")
        sys.exit(1)
    
    if torch.cuda.device_count() == 0:
        print("CUDA found but not device visible")
        sys.exit(1)

    with torch.no_grad():
        aggregate_visits_w_spy = read_npz(os.path.join(aggregate_visit_matrix_dir, "aggregate_visit_matrix.npz"))
        aggregate_visits_w = coo_to_tensor_torch(aggregate_visits_w_spy)
        aggregate_visits_w = aggregate_visits_w.cuda()

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
            cbg_marginals_u_t_np = read_npy(cbg_marginal_filepath)
            cbg_marginals_u_t = torch.from_numpy(cbg_marginals_u_t_np)
            cbg_marginals_u_t = cbg_marginals_u_t.cuda()
            poi_marginal_v_t_spy = read_npz(poi_marginal_filepath)
            poi_marginal_v_t = coo_to_tensor_torch(poi_marginal_v_t_spy)
            poi_marginal_v_t = poi_marginal_v_t.cuda()
            
            """
            Parallel(n_jobs=4)(
                (delayed(ipfp)(day, hour, aggregate_visits_w, cbg_marginals_u_t[:, hour], poi_marginal_v_t.getcol(hour), day_dir) for hour in range(cbg_marginals_u_t.shape[1]))
            )
            """
            for hour in range(cbg_marginals_u_t.shape[1]):
                ipfp(day, hour, aggregate_visits_w, cbg_marginals_u_t[:, hour], coo_get_col_to_dense(poi_marginal_v_t, hour), day_dir)

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