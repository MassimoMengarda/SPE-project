import torch
import numpy as np
from ..data_extraction_and_preprocessing.sparse_vector_utils import sparse_dense_vector_mul

class CounterMeasure:
    def __init__(self, simulation):
        self.total_peoples_in_bar_without_changes = 0.0
        self.supposed_people_in_bars_during_closing = 0.0
        self.simulation = simulation
        pass
    
    def init_week(self):
        
        pass

    def apply(self, simulation_time, original_hour_movement_table, poi_categories):
        mask = poi_categories == 168 # 168: Food services and drinking places
        total_period_people = torch.sum(sparse_dense_vector_mul(torch.index_select(original_hour_movement_table, 0, torch.from_numpy(np.where(mask))[0]), self.simulation.cbgs_population))
        self.total_peoples_in_bar_without_changes += total_period_people
        if simulation_time.hour() >= 18:
            self.supposed_people_in_bars_during_closing += total_period_people
            new_hour_movement_table = torch.index_select(original_hour_movement_table, 0, torch.from_numpy(np.where(~mask)[0]))
            
            

            sectors_loss = [(15, 1500.0), (14, 4.5)] # len 250

            return new_hour_movement_table, sectors_loss

    # TODO
    # Compute the number of customers in original_hour_movement_table
    #       x => sum over the row of the original_hour_movement_table
    # Compute the number of customers lost due to countermeasure
    #       y => sum over the row of the new_hour_movement_table - x
    
    # At the end of the week, sum up all the losses and compute the actual sector loss
    #       for each losses => total_loss += hourly_sector_loss
    # Run the sectors simulation for each sector loss
    #       for each sector_loss => graph.add_loss_to_edge