class CounterMeasure:
    def __init__(self):
        pass
        
    def countermeasure(self, hour, hour_movement_table, poi_categories):
        sectors_loss = [0,0,5000,0,0,0,0,0] # len 250
        return hour_movement_table, sectors_loss