from .close_activity import GeneralCounterMeasure

class CounterMeasure(GeneralCounterMeasure):
    def __init__(self, simulation):
        super().__init__(simulation, poi_categories=[168], closing_hour=18)
    
    def init_week(self):
        super().init_week()

    def apply(self, simulation_time, original_hour_movement_table):
        return super().apply(simulation_time, original_hour_movement_table)

    def end_simulation(self):
        loss_results = []
        for poi_category in self.poi_categories:
            sector_fd = self.simulation.sectors_graph.get_edge_initial_exchange_total(poi_category)
            sector_loss = (self.supposed_people_inside_during_closing / self.total_people_inside_without_changes) * sector_fd
            sector_loss *= 0.7
            loss_results.append((poi_category, sector_loss))
        return loss_results