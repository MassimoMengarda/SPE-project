import argparse
import datetime
import os
import time
from importlib import import_module

import numpy as np
import torch

from data_extraction_and_preprocessing.utils import (read_csv, read_npy)
from sectors_graph import Graph
from data_extraction_and_preprocessing.sparse_vector_utils import sparse_dense_vector_mul

class Model:
    def __init__(self, cbgs_population, ipfp_dir, pois_dwell_dir, poi_categories, sector_graph_filepath, counter_measure_filepath, n_pois, pois_area, b_bases=[0.0126], psis=[2700], p_0s=[0.000495], p_dead=0.02, t_e=96, t_i=84, batch=1):
        self.b_bases = b_bases
        self.psis = psis
        self.p_0s = p_0s
        self.p_dead = p_dead
        self.t_e = t_e
        self.t_i = t_i
        
        self.n_pois = n_pois
        self.pois_area = torch.reshape(pois_area, (pois_area.shape[0], 1))
        self.n_cbgs = cbgs_population.shape[0]
        self.cbgs_population = torch.reshape(cbgs_population, (1, 1, cbgs_population.shape[0]))
        # self.cbgs_population = cbgs_population

        self.pois_dwell_dir = pois_dwell_dir
        self.ipfp_dir = ipfp_dir
        self.batch = batch
        self.poi_categories = poi_categories

        self.sectors_graph = Graph()
        self.sectors_graph.load_data(sector_graph_filepath)

        self.counter_measure_filepath = counter_measure_filepath

    def simulate(self, simulation_start_datetime, simulation_end_datetime):
        # Rescale the economic data to the simulation time instead of whole year
        self.sectors_graph.scale_sector_graph(simulation_start_datetime, simulation_end_datetime)

        # Import and load all the counter-measures
        countermeasures = []
        with open(self.counter_measure_filepath, "r") as f:
            countermeasures = f.readlines()

        countermeasures_classes = []
        for i in countermeasures:
            if not i.startswith("#"):
                module = import_module("countermeasures." + i.strip())
                countermeasures_classes.append(getattr(module, "CounterMeasure"))
        
        # Initialize the simulation (N and SEIR model)
        cbgs_population_repeated = torch.tile(self.cbgs_population[None, :, :], (self.batch, 1, 1))

        probs_cbg_e = torch.tile(self.p_0s[:, None, None], (1, cbgs_population_repeated.shape[1], cbgs_population_repeated.shape[2])) # , dtype=torch.float32, device="cuda"

        cbg_e = torch.binomial(count=cbgs_population_repeated.float(), prob=probs_cbg_e)
        
        cbg_s = cbgs_population_repeated - cbg_e
        cbg_i = torch.zeros((self.batch, 1, self.n_cbgs), dtype=torch.float32, device="cuda")
        cbg_r_dead = torch.zeros((self.batch, 1, self.n_cbgs), dtype=torch.float32, device="cuda")
        cbg_r_alive = torch.zeros((self.batch, 1, self.n_cbgs), dtype=torch.float32, device="cuda")
        
        # Initialize the simulation time
        last_week_loaded = datetime.datetime(1990, 1, 1).date() # Dummy value
        simulation_time = simulation_start_datetime
        
        total_io_time = 0
        total_compute_time = 0
        weekly_pois_dwell = None
        
        # Initialize all the counter-measures
        initialized_countermeasures = []
        for countermeasure in countermeasures_classes:
            initialized_countermeasures.append(countermeasure(self))
            
        # Run the simulation until the end or until there are no cases anymore
        while simulation_time <= simulation_end_datetime:
            
            week_num = simulation_time.weekday()
            week_start_date = (simulation_time - datetime.timedelta(days=week_num)).date()
            week_string = week_start_date.strftime("%Y-%m-%d")

            # Load the data for the week
            if week_start_date != last_week_loaded:
                weekly_pois_dwell_np = read_npy(os.path.join(self.pois_dwell_dir, week_string + ".npy"))
                weekly_pois_dwell = torch.from_numpy(weekly_pois_dwell_np).cuda()
                weekly_pois_dwell = torch.reshape(weekly_pois_dwell, (weekly_pois_dwell.shape[0], 1))
                weekly_pois_area_ratio = torch.square(weekly_pois_dwell) / self.pois_area
                last_week_loaded = week_start_date
                
                for countermeasure in initialized_countermeasures:
                    countermeasure.init_week()
            
            # Compute the changes in simulation time
            time_difference_from_week_start = simulation_time - datetime.datetime.combine(week_start_date, datetime.datetime.min.time())
            week_t = time_difference_from_week_start.days * 24 + time_difference_from_week_start.seconds // 3600
            start_time = time.time()
            w_ij = torch.load(os.path.join(self.ipfp_dir, week_string, "{:0>3d}.pth".format(week_t))).cuda()
            w_ij = w_ij.coalesce()
            total_io_time += time.time() - start_time

            # Apply all the counter-measures previously defined
            for countermeasure in initialized_countermeasures:
                w_ij, sectors_loss = countermeasure.apply(simulation_time, w_ij)
                for sector, loss in sectors_loss:
                    self.sectors_graph.add_loss_to_edge(sector, loss)

            start_time = time.time()
            # Compute the new parameters (SEIR model)
            delta_ci = self.get_delta_ci(cbg_i)
            delta_pj = self.get_delta_pj(cbg_i, w_ij, weekly_pois_area_ratio)

            cbg_new_e = self.get_new_e(cbg_s, delta_pj, delta_ci, w_ij)
            cbg_new_i = self.get_new_i(cbg_e)
            cbg_new_r_dead, cbg_new_r_alive = self.get_new_r(cbg_i)

            # Update the current SEIR numbers 
            cbg_r_dead = cbg_r_dead + cbg_new_r_dead
            cbg_r_alive = cbg_r_alive + cbg_new_r_alive
            cbg_i = cbg_i - (cbg_new_r_dead + cbg_new_r_alive) + cbg_new_i
            cbg_e = cbg_e - cbg_new_i + cbg_new_e
            cbg_s = cbg_s - cbg_new_e

            total_compute_time += time.time() - start_time

            # Yield the results hour by hour
            yield simulation_time, week_string, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive, cbg_new_i

            # Kill the simulation if there are no new cases
            if not torch.any(cbg_e + cbg_i):
                print(f"Simulation of week {week_string} terminanted at hour {week_t} because there were no more infectious")
                break
            
            simulation_time += datetime.timedelta(hours=1)
        
        # Compute the actual economic loss
        for countermeasure in initialized_countermeasures:
                sectors_loss = countermeasure.end_simulation()
                for sector, loss in sectors_loss:
                    self.sectors_graph.add_loss_to_edge(sector, loss)
        
        print("Compute time: {}, IO Time: {}".format(total_compute_time, total_io_time))

    def get_delta_ci(self, cbg_i):
        return self.b_bases[:, None, None] * torch.div(cbg_i, self.cbgs_population)

    def get_delta_pj(self, cbg_i, w_ij, weekly_pois_area_ratio):
        delta_pj = torch.empty((self.batch, weekly_pois_area_ratio.shape[0], weekly_pois_area_ratio.shape[1]), dtype=torch.float32, device="cuda")
        for batch in range(self.batch):
            delta_pj[batch] = torch.multiply(weekly_pois_area_ratio, torch.sparse.sum(sparse_dense_vector_mul(w_ij, cbg_i[batch] / self.cbgs_population[0]), dim=1).to_dense()[:, None])
        return delta_pj

    def get_new_e(self, cbg_s, delta_pj, delta_ci, w_ij):
        poisson_args = torch.empty_like(cbg_s)
        for batch in range(self.batch):
            poisson_args[batch] = torch.multiply((cbg_s[batch] / self.cbgs_population), torch.sparse.sum(sparse_dense_vector_mul(w_ij, delta_pj[batch]), dim=0).to_dense())
        poisson = torch.poisson(self.psis[:, None, None] * poisson_args)
        binom = torch.binomial(count=cbg_s, prob=delta_ci)
        return torch.minimum(cbg_s, poisson + binom)

    def get_new_i(self, cbg_e):
        binom_distr = torch.distributions.binomial.Binomial(total_count=cbg_e, probs=(1 / self.t_e))
        return binom_distr.sample().cuda()

    def get_new_r(self, cbg_i):
        new_r = torch.binomial(count=cbg_i, prob=torch.full(cbg_i.shape, 1 / self.t_i, dtype=torch.float32, device="cuda"))
        new_r_dead = torch.binomial(count=new_r, prob=torch.full(new_r.shape, self.p_dead, dtype=torch.float32, device="cuda"))
        return new_r_dead, new_r - new_r_dead

def save_result(output_dir, week, t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive):
    array_to_save = np.asarray([cbg_s.cpu().numpy(), cbg_e.cpu().numpy(), cbg_i.cpu().numpy(), cbg_r_dead.cpu().numpy(), cbg_r_alive.cpu().numpy()])

    dir_path = os.path.join(output_dir, week)
    os.makedirs(dir_path, exist_ok=True)
    filename = "{:0>3d}.npy".format(t)
    filepath = os.path.join(dir_path, filename)

    print(f"Saving result of week {week} at time {t} in {filepath}")
    np.save(filepath, array_to_save)

def main(info_dir, ipfp_dir, dwell_dir, sector_graph_filepath, counter_measure_filepath, output_dir):
    with torch.no_grad():
        poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
        n_pois = len(poi_index.index)
        poi_categories = read_csv(os.path.join(info_dir, "poi_categories_with_io_sector.csv"))
        cbgs_population_np = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
        cbgs_population = torch.from_numpy(cbgs_population_np)
        cbgs_population = cbgs_population.cuda().float()
        pois_area_np = read_npy(os.path.join(info_dir, "poi_area.npy"))
        pois_area = torch.from_numpy(pois_area_np)
        pois_area = pois_area.cuda()
        
        simulation_start = datetime.datetime(2020, 3, 2, 0) # TODO pass as arguments
        simulation_end = datetime.datetime(2020, 3, 6, 23) # TODO pass as arguments
        batch = 10 # TODO pass as arguments

        b_bases = torch.full((batch,), 0.0126, device='cuda')
        psis = torch.full((batch,), 2700, device='cuda')
        p_0s = torch.full((batch,), 0.000495, device='cuda')

        m = Model(cbgs_population, ipfp_dir, dwell_dir, torch.from_numpy(poi_categories["io_sector"].to_numpy()).cuda(), sector_graph_filepath, counter_measure_filepath, n_pois, pois_area, b_bases=b_bases, psis=psis, p_0s=p_0s, t_e=96, t_i=84, batch=batch)
        
        for simulation_time, week_string, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive, _ in m.simulate(simulation_start, simulation_end):
            print(f"week_string {week_string}, week_t {week_t}")
            save_result(output_dir, week_string, week_t, cbg_s, cbg_e, cbg_i, cbg_r_dead, cbg_r_alive)
        
        m.sectors_graph.save_sectors_graph(os.path.join(output_dir, "sector_graph.npy"))
        m.sectors_graph.print_inputs()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("ipfp_directory", type=str, help="the directory where the ipfp matrixes are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("delta_pj_directory", type=str, help="the directory where the dwell matrixes are stored")
    parser.add_argument("sector_graph_filepath", type=str, help="the path to the I/O tables dataset")
    parser.add_argument("counter_measure_filepath", type=str, help="the path to the counter-measures list")
    parser.add_argument("output_directory", type=str, help="the directory where store the result")

    args = parser.parse_args()
    ipfp_dir = args.ipfp_directory
    info_dir = args.info_directory
    dwell_dir = args.dwell_directory
    sector_graph_filepath = args.sector_graph_filepath
    counter_measure_filepath = args.counter_measure_filepath
    output_dir = args.output_directory
    
    main(info_dir, ipfp_dir, dwell_dir, sector_graph_filepath, counter_measure_filepath, output_dir)
    