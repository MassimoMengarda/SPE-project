from .close_activity import GeneralCounterMeasure

class CounterMeasure(GeneralCounterMeasure):
    def __init__(self, simulation):
        super().__init__(simulation, poi_category=168, closing_hour=18)
    
    def init_week(self):
        super().init_week()

    def apply(self, simulation_time, original_hour_movement_table):
        return super().apply(simulation_time, original_hour_movement_table)

    def end_simulation(self):
        return super().end_simulation()