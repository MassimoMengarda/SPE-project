import argparse
import datetime
import math
import os
import sys

import numpy as np
import torch
import pandas as pd

from data_extraction_and_preprocessing.utils import read_csv, read_npy
from simulation_torch import Model

def converter(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d")

def main(simulation_parameters_filepath, info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir):
    with torch.no_grad():
        poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
        cases_df = read_csv(cases_filepath, converters={"date": converter})
        cases = cases_df.groupby(["date"]).sum()
        n_pois = len(poi_index.index)
        cbgs_population_np = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
        cbgs_population = torch.from_numpy(cbgs_population_np).cuda().float()
        pois_area = read_npy(os.path.join(info_dir, "poi_area.npy"))
        pois_area = torch.from_numpy(pois_area).cuda()

        os.makedirs(output_dir, exist_ok=True)
        
        best_params = (sys.float_info.max, -1, -1, -1)

        confirmed_new_cases_proportion = 0.1 # r_c
        n_simulation = 10
        delta_c = 168
        
        simulation_start = datetime.datetime(2020, 3, 2, 0)
        # simulation_end = datetime.datetime(2020, 3, 2, 23)
        simulation_end = datetime.datetime(2020, 5, 10, 23)
        batch = 10

        output_filepath = os.path.join(output_dir, "rmse_result.csv")
                        
        if not os.path.isfile(output_filepath):
            with open(output_filepath, "a") as f_handle:
                f_handle.write("b_base;psi;p_0;rmse\n")
        
        parameters_df = pd.read_csv(simulation_parameters_filepath)

        rows_per_simulation = 1
        current_rows = 1
        b_bases = []
        psis = []
        p_0s = []

        b_bases_batch = []
        psis_batch = []
        p_0s_batch = []
        for i, line in parameters_df.iterrows():
            if current_rows <= rows_per_simulation:
                # print("Add")
                b_bases.extend([line["b_base"] for i in range(batch)])
                psis.extend([line["psi"] for i in range(batch)])
                p_0s.extend([line["p_0"] for i in range(batch)])

                print("Computing parameters b_base {} psi {} p_0 {}".format(line["b_base"], line["psi"], line["p_0"]))
                
                b_bases_batch.append(line["b_base"])
                psis_batch.append(line["psi"])
                p_0s_batch.append(line["p_0"])

                if current_rows != rows_per_simulation:
                    current_rows += 1
                    continue
            
            b_bases_torch = torch.FloatTensor(b_bases).cuda()
            psis_torch = torch.FloatTensor(psis).cuda()
            p_0s_torch = torch.FloatTensor(p_0s).cuda()
            
            day_new_cases = [[[0] for i in range(batch * rows_per_simulation)] for _ in range(24 + delta_c)]
            rmse_sum = torch.zeros((batch * rows_per_simulation, ), dtype=torch.float32)

            m = Model(cbgs_population, ipfp_dir, dwell_dir, None, n_pois, pois_area, b_bases_torch, psis_torch, p_0s_torch, t_e=96, t_i=84, batch=rows_per_simulation * batch)

            days_of_simulation = 0
            for simulation_time, week_string, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive, cbg_new_i in m.simulate(simulation_start, simulation_end):
                day_new_cases.pop(0)
                # print(cbg_new_i.shape)
                # print(torch.sum(cbg_new_i, axis=2).shape)
                day_new_cases.append(torch.sum(cbg_new_i, axis=2).cpu().numpy()) # TODO check size (10, 1, 140k)
                
                if simulation_time.hour == 0:
                    cases_index = simulation_time - datetime.timedelta(days=1)
                    if cases_index in cases.index:
                        certified_new_cases = cases.loc[cases_index]["cases"]
                    else:
                        certified_new_cases = 0
                    estimated_confirmed_new_cases = confirmed_new_cases_proportion * np.sum(np.asarray(day_new_cases[0:24]), axis=0)
                    rmse_sum = rmse_sum + (estimated_confirmed_new_cases - certified_new_cases) ** 2 
                    days_of_simulation += 1
            
            rmse = np.sqrt(rmse_sum / days_of_simulation)
            rmse_for_parameters = np.split(rmse, rows_per_simulation)

            with open(output_filepath, "a") as f_handle:
                for idx, single_rmse in enumerate(rmse_for_parameters):
                    average_rmse = np.average(single_rmse) # sum(rmse_sum) / rmse_sum.shape[0]
                    print(f"rmse {average_rmse} with b_base {b_bases_batch[idx]}, psi {psis_batch[idx]} p_0 {p_0s_batch[idx]}")
                    
                    f_handle.write("{};{};{};{}\n".format(b_bases_batch[idx], psis_batch[idx], p_0s_batch[idx], average_rmse))
                    f_handle.flush()

                    if (best_params[0] > average_rmse):
                        best_params = (average_rmse, b_bases_batch[idx], psis_batch[idx], p_0s_batch[idx])
            
            b_bases = []
            psis = []
            p_0s = []

            b_bases_batch = []
            psis_batch = []
            p_0s_batch = []

            current_rows = 1

        print("FINAL RESULT: ", best_params)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("simulation_parameters_filepath", type=str, help="the filepath where the simulation to run are stored")
    parser.add_argument("ipfp_directory", type=str, help="the directory where the ipfp matrixes are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("dwell_directory", type=str, help="the directory where the dwell matrixes are stored")
    parser.add_argument("cases_filepath", type=str, help="the filepath where the number of cases are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the result")
    args = parser.parse_args()
    simulation_parameters_filepath = args.simulation_parameters_filepath
    ipfp_dir = args.ipfp_directory
    info_dir = args.info_directory
    dwell_dir = args.dwell_directory
    cases_filepath = args.cases_filepath
    output_dir = args.output_directory
    
    main(simulation_parameters_filepath, info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir)
