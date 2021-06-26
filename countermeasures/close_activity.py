import torch
import numpy as np
from data_extraction_and_preprocessing.sparse_vector_utils import sparse_dense_vector_mul

class GeneralCounterMeasure:
    def __init__(self, simulation, poi_categories, closing_hour=0):
        self.total_people_inside_without_changes = 0.0
        self.supposed_people_inside_during_closing = 0.0
        self.simulation = simulation
        
        self.closing_hour = closing_hour
        self.poi_categories = poi_categories
    
    def init_week(self):
        self.supposed_people_inside_during_closing += 0.0

    def apply(self, simulation_time, original_hour_movement_table):
        mask = torch.zeros_like(self.simulation.poi_categories, dtype=torch.bool, device='cuda')
        for poi_category in self.poi_categories:
            mask = torch.logical_or(mask, self.simulation.poi_categories == poi_category)
        people_inside_poi = torch.sparse.sum(sparse_dense_vector_mul(original_hour_movement_table, self.simulation.cbgs_population), dim=1).to_dense()
        people_inside_activity_in_hour = torch.sum(people_inside_poi[mask]).item()
        self.total_people_inside_without_changes += people_inside_activity_in_hour
        sectors_loss = []
        
        if simulation_time.hour >= self.closing_hour:
            self.supposed_people_inside_during_closing += people_inside_activity_in_hour
            new_hour_movement_table = sparse_dense_vector_mul(original_hour_movement_table, torch.reshape(torch.logical_not(mask), (mask.shape[0], 1)))
            return new_hour_movement_table, sectors_loss
        
        return original_hour_movement_table, sectors_loss
    
    def end_simulation(self):
        loss_results = []
        for poi_category in self.poi_categories:
            sector_fd = self.simulation.sectors_graph.get_edge_initial_exchange_total(poi_category)
            sector_loss = (self.supposed_people_inside_during_closing / self.total_people_inside_without_changes) * sector_fd
            loss_results.append((poi_category, sector_loss))
        return loss_results
