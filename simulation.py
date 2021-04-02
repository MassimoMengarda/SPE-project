import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo

from data_extraction_and_preprocessing.utils import read_csv, read_npy, read_npz
import datetime

class Model:
    def __init__(self, cbgs_population, ipfp_dir, pois_dwell_dir, output_dir, n_pois, pois_area, weeks, b_base=0.0126, psi=2700, p_0=0.000495, p_dead=0.02, t_e=96, t_i=84):
        self.weeks = weeks
        self.b_base = b_base
        self.psi = psi
        self.p_0 = p_0
        self.p_dead = p_dead
        self.t_e = t_e
        self.t_i = t_i
        
        self.n_pois = n_pois
        self.pois_area = np.reshape(pois_area, (pois_area.shape[0], 1))
        self.n_cbgs = len(cbgs_population)
        self.cbgs_population = np.reshape(cbgs_population, (1, cbgs_population.shape[0]))

        self.pois_dwell_dir = pois_dwell_dir
        self.ipfp_dir = ipfp_dir
        self.output_dir = output_dir

    def simulate(self, simulation_start_datetime, simulation_end_datetime, save=True, generator=False):
        cbg_e = np.random.binomial(self.cbgs_population, self.p_0)
        cbg_s = self.cbgs_population - cbg_e
        cbg_i = np.zeros((1, self.n_cbgs), dtype=np.int32)
        cbg_r_dead = np.zeros((1, self.n_cbgs), dtype=np.int32)
        cbg_r_alive = np.zeros((1, self.n_cbgs), dtype=np.int32)
        
        # total_t = 0
        last_week_loaded = datetime.date(1990, 1, 1).date() # Dummy value
        simulation_time = simulation_start_datetime

        simulation_timedelta = simulation_start_datetime - simulation_end_datetime
        # total_simulation_time = simulation_timedelta.days * 24 + simulation_timedelta.seconds // 3600

        weekly_pois_dwell = None
        while simulation_time < simulation_end_datetime:
            week_num = simulation_time.weekday() #
            week_start_date = (simulation_time - datetime.timedelta(days=week_num)).date()
            if week_start_date != last_week_loaded:
                weekly_pois_dwell = read_npy(os.path.join(self.pois_dwell_dir, week_start_date.strfmt("%Y-%m-%d") + ".npy"))
                weekly_pois_dwell = np.reshape(weekly_pois_dwell, (weekly_pois_dwell.shape[0], 1))
                last_week_loaded = week_start_date
            
            time_difference_from_week_start = week_start_date - simulation_time
            week_t = time_difference_from_week_start.days * 24 + time_difference_from_week_start.seconds // 3600
            week_total_time = 24 * 7

            w_ij = read_npz(os.path.join(self.ipfp_dir, week_start_date.strfmt("%Y-%m-%d"), "{:0>3d}.npz".format(week_t)))

            # Compute the new parameters
            delta_ci = self.get_delta_ci(cbg_i)
            delta_pj = self.get_delta_pj(cbg_i, w_ij, weekly_pois_dwell)

            cbg_new_e = self.get_new_e(cbg_s, delta_pj, delta_ci, w_ij)
            cbg_new_i = self.get_new_i(cbg_e)
            cbg_new_r_dead, cbg_new_r_alive = self.get_new_r(cbg_i)

            # Update the current SEIR numbers 
            cbg_r_dead = cbg_r_dead + cbg_new_r_dead
            cbg_r_alive = cbg_r_alive + cbg_new_r_alive
            cbg_i = cbg_i - (cbg_new_r_dead + cbg_new_r_alive) + cbg_new_i
            cbg_e = cbg_e - cbg_new_i + cbg_new_e
            cbg_s = cbg_s - cbg_new_e

            if save:
                self.save_result(week_start_date, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive)
                
            if generator:
                yield cbg_e, cbg_s, cbg_i, cbg_r_dead, cbg_r_alive, cbg_new_e, cbg_new_i

            if not np.any(cbg_e + cbg_i):
                print(f"Simulation of week {week_start_date} terminanted at hour {week_t} because there were no more infectious")
                break
            
            total_t += datetime.timedelta(hours=1)

    def get_delta_ci(self, cbg_i):
        return self.b_base * (cbg_i / self.cbgs_population)

    def get_delta_pj(self, cbg_i, w_ij, weekly_pois_dwell):
        return np.multiply((np.square(weekly_pois_dwell) / self.pois_area), w_ij.multiply(cbg_i / self.cbgs_population).sum(axis=1))

    def get_new_e(self, cbg_s, delta_pj, delta_ci, w_ij):
        poisson = np.random.poisson(self.psi * np.multiply((cbg_s / self.cbgs_population), w_ij.multiply(delta_pj).sum(axis=0)))
        binom = np.random.binomial(cbg_s, delta_ci)
        return np.minimum(cbg_s, poisson + binom) # TODO check if it is correct

    def get_new_i(self, cbg_e):
        return np.random.binomial(cbg_e, 1 / self.t_e)

    def get_new_r(self, cbg_i):
        new_r = np.random.binomial(cbg_i, 1 / self.t_i) # TODO adjust param
        new_r_dead = np.random.binomial(new_r, self.p_dead)
        return new_r_dead, new_r - new_r_dead

    def save_result(self, week, t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive):
        array_to_save = np.asarray([cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive])

        dir_path = os.path.join(self.output_dir, week)
        os.makedirs(dir_path, exist_ok=True)
        filename = "{:0>3d}.npy".format(t)
        filepath = os.path.join(dir_path, filename)

        print(f"Saving result of week {week} at time {t} in {filepath}")
        np.save(filepath, array_to_save)

def main(info_dir, ipfp_dir, dwell_dir, output_dir):
    poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    n_pois = len(poi_index.index)
    cbgs_population = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
    pois_area = read_npy(os.path.join(info_dir, "poi_area.npy"))
    weeks = ["2019-01-07"]
    
    m = Model(cbgs_population, ipfp_dir, dwell_dir, output_dir, n_pois, pois_area, weeks, b_base=0.0126, psi=2700, p_0=0.000495, t_e=96, t_i=84)
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
    
    main(info_dir, ipfp_dir, dwell_dir, output_dir)
    