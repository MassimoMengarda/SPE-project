import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo

from data_extraction_and_preprocessing.utils import read_csv, read_npy, read_npz

# βbase ranges from 0.0012 to 0.024 => 0.0126
# ψ ranges from 515 to 4,886 => 2700
# p0 ranges from 10−5 to 10−2 => 0.000495

# δE = 96 h (refs. 20,58) and δI = 84 h (ref. 20) based

class Model:
    def __init__(self, cbgs_population, ipfp_dir, pois_dwell_dir, n_pois, pois_area, weeks, b_base=0.0126, psi=2700, p_0=0.000495, t_e=96, t_i=84):
        self.t = 0
        self.weeks = weeks
        self.b_base = b_base
        self.psi = psi
        self.p_0 = p_0
        self.t_e = t_e
        self.t_i = t_i
        
        self.n_pois = n_pois
        self.pois_area = np.reshape(pois_area, (pois_area.shape[0], 1))
        self.n_cbgs = len(cbgs_population)
        self.cbgs_population = np.reshape(cbgs_population, (1, cbgs_population.shape[0]))

        self.pois_dwell_dir = pois_dwell_dir
        self.ipfp_dir = ipfp_dir

    def simulate(self):
        cbg_e = np.random.binomial(self.cbgs_population, self.p_0)
        cbg_s = self.cbgs_population - cbg_e
        cbg_i = np.zeros((1, self.n_cbgs))
        cbg_r = np.zeros((1, self.n_cbgs))
        
        for week in self.weeks:
            weekly_pois_dwell = read_npy(os.path.join(self.pois_dwell_dir, week + ".npy"))
            weekly_pois_dwell = np.reshape(weekly_pois_dwell, (weekly_pois_dwell.shape[0], 1))
            week_time = 24 * 7
            
            while self.t < week_time:
                w_ij = read_npz(os.path.join(self.ipfp_dir, week, "{:0>2d}.npz".format(self.t)))

                delta_ci = self.get_delta_ci(cbg_i)
                delta_pj = self.get_delta_pj(cbg_i, w_ij, weekly_pois_dwell)

                cbg_new_e = self.get_new_e(cbg_s, cbg_i, delta_pj, delta_ci, w_ij)
                cbg_new_i = self.get_new_i(cbg_e)
                cbg_new_r = self.get_new_r(cbg_i)

                self.t += 1

    def get_delta_ci(self, cbg_i):
        return self.b_base * (cbg_i / self.cbgs_population)

    def get_delta_pj(self, cbg_i, w_ij, weekly_pois_dwell): # TODO result matrix  = [[nan], [nan], [nan], ...,[nan]]
        return np.multiply((np.square(weekly_pois_dwell) / self.pois_area), w_ij.multiply(cbg_i / self.cbgs_population).sum(axis=1))

    def get_new_e(self, cbg_s, cbg_i, delta_pj, delta_ci, w_ij):
        pois = np.random.poisson(self.psi * (cbg_s / self.cbgs_population) * np.sum(delta_pj * w_ij))
        binom = np.random.binomial(cbg_s, delta_ci)
        return pois + binom

    def get_new_i(self, cbg_e):
        return np.random.binomial(cbg_e, 1 / self.t_e)

    def get_new_r(self, cbg_i):
        return np.random.binomial(cbg_i, 1 / self.t_i)

def main(info_dir, ipfp_dir, dwell_dir):
    poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    n_pois = len(poi_index.index)
    cbgs_population = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
    pois_area = read_npy(os.path.join(info_dir, "poi_area.npy"))
    weeks = ["2019-01-07"]
    
    m = Model(cbgs_population, ipfp_dir, dwell_dir, n_pois, pois_area, weeks, b_base=0.0126, psi=2700, p_0=0.000495, t_e=96, t_i=84)
    m.simulate()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("ipfp_directory", type=str, help="the directory where the ipfp matrixes are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("dwell_directory", type=str, help="the directory where the dwell matrixes are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the index result")
    args = parser.parse_args()
    ipfp_dir = args.ipfp_directory
    info_dir = args.info_directory
    dwell_dir = args.dwell_directory
    output_dir = args.output_directory
    
    # TODO use output directory
    main(info_dir, ipfp_dir, dwell_dir)
    