import torch
import numpy as np

class CounterMeasure:
    def __init__(self):
        pass
    
    def init_week(self):
        
        pass

    def apply(self, simulation_time, original_hour_movement_table, poi_categories):
        if simulation_time.hour() >= 18:
            mask = ~(poi_categories == 168) # 168: Food services and drinking places
            
            hour_bar_movements = torch.index_select(original_hour_movement_table, 0, mask)
            hour_bar_movements
            new_hour_movement_table = torch.index_select(original_hour_movement_table, 0, torch.from_numpy(np.where(mask)[0]))
            
            

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