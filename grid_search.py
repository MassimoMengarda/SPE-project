import argparse
import datetime
import math
import os
import sys

import numpy as np

from data_extraction_and_preprocessing.utils import read_csv, read_npy
from simulation import Model

def converter(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d")

def main(info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir):
    poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    cases_df = read_csv(cases_filepath, converters={"date": converter})
    cases = cases_df.groupby(["date"]).sum()
    n_pois = len(poi_index.index)
    cbgs_population = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
    pois_area = read_npy(os.path.join(info_dir, "poi_area.npy"))

    os.makedirs(output_dir, exist_ok=True)
    
    b_base_s = np.linspace(0.0012, 0.024, num=10)
    psi_s = np.linspace(515, 4886, num=15)
    p_0_s = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]

    best_params = (sys.float_info.max, -1, -1, -1)

    confirmed_new_cases_proportion = 0.1 # r_c
    n_simulation = 10
    delta_c = 168
    
    simulation_start = datetime.datetime(2020, 3, 2, 0)
    simulation_end = datetime.datetime(2020, 5, 10, 23)
    batch = 10

    output_path = os.path.join(output_dir, "rmse_result.csv")
                    
    if not os.path.isfile(output_path):
        with open(output_path, "a") as f_handle:
            f_handle.write("b_base;psi;p_0;rmse\n")

    for b_base in b_base_s:
        for psi in psi_s:
            for p_0 in p_0_s:
                print(f"Computing parameters b_base {b_base} psi {psi} p_0 {p_0}")
                day_new_cases = [0 for _ in range(24 + delta_c)]
                
                print(f"Running simulation number {i + 1}")
                rmse_sum = np.zeros((batch, 1), dtype=np.float32)

                m = Model(cbgs_population, ipfp_dir, dwell_dir, None, n_pois, pois_area, b_base, psi, p_0, t_e=96, t_i=84, batch=batch)

                days_of_simulation = 0
                for simulation_time, week_string, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive, cbg_new_i in m.simulate(simulation_start, simulation_end):
                    day_new_cases.pop(0)
                    day_new_cases.append(np.sum(cbg_new_i, axis=2)) # TODO check size (10, 1, 140k)
                    
                    if simulation_time.hour == 0:
                        cases_index = simulation_time - datetime.timedelta(days=1)
                        if cases_index in cases.index:
                            certified_new_cases = cases.loc[cases_index]["cases"]
                        else:
                            certified_new_cases = 0
                        estimated_confirmed_new_cases = confirmed_new_cases_proportion * np.sum(day_new_cases[0:24], axis=1)
                        rmse_sum = rmse_sum + (estimated_confirmed_new_cases - certified_new_cases) ** 2 
                        days_of_simulation += 1
                
                rmse = np.sqrt(rmse_sum / days_of_simulation)
                average_rmse = np.mean(rmse) # sum(rmse_sum) / rmse_sum.shape[0]
                print(f"rmse {average_rmse} with b_base {b_base}, psi {psi} p_0 {p_0}")

                with open(output_path, "a") as f_handle:
                    f_handle.write("{};{};{};{}\n".format(b_base, psi, p_0, average_rmse))
                    f_handle.flush()

                if (best_params[0] > average_rmse):
                    best_params = (average_rmse, b_base, psi, p_0)

    print("FINAL RESULT: ", best_params)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("ipfp_directory", type=str, help="the directory where the ipfp matrixes are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("dwell_directory", type=str, help="the directory where the dwell matrixes are stored")
    parser.add_argument("cases_filepath", type=str, help="the filepath where the number of cases are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the result")
    args = parser.parse_args()
    ipfp_dir = args.ipfp_directory
    info_dir = args.info_directory
    dwell_dir = args.dwell_directory
    cases_filepath = args.cases_filepath
    output_dir = args.output_directory
    
    main(info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir)
