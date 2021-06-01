from data_extraction_and_preprocessing.utils import read_csv
import networkx as nx
import matplotlib.pyplot as plt
import sys

# TODO: inverse how the class work
class Node:
    def __init__(self, category_id, outputs, initial_input_sum):
        self.category_id = category_id
        self.outputs = outputs # Edges
        self.final_input_sum = 0
        self.initial_input_sum = initial_input_sum

class Edge:
    def __init__(self, initial_exchange_total, intrasector):
        self.initial_exchange_total = initial_exchange_total
        self.current_value = initial_exchange_total
        self.loss = 0.0
        self.intrasector = intrasector

class Graph:
    def __init__(self, delta=0.0005):
        self.nodes = {}
        self.delta = delta

    def load_data(self, io_filepath):
        io_df = read_csv(io_filepath, sep=",", index_col="Sector")
        for idx, io_row in io_df.iterrows():
            idx = str(idx).strip()
            outputs = {}

            for output_category, value in io_row.iteritems():
                if value > sys.float_info.epsilon:
                    outputs[str(output_category).strip()] = Edge(value, output_category == idx)
            
            self.nodes[idx] = Node(idx, outputs, io_df[idx].sum())
    
    def add_loss_impact(self, input_sector, input_loss): # peso effettivo in entrata
        assert(input_loss <= self.nodes[input_sector].initial_input_sum)
        elements = [(input_sector, input_loss)]
        
        intrasector_visited = {}
        for sector in self.nodes:
            intrasector_visited[sector] = False
        
        while len(elements) > 0:
            sector, loss = elements.pop(0)
            node = self.nodes[sector]
            percentage = loss / node.initial_input_sum

            if percentage > self.delta: # if the percentage is irrelevant, do not compute the changes
                for output_cat_id in node.outputs:
                    if node.outputs[output_cat_id].intrasector:
                        if intrasector_visited[output_cat_id]:
                            continue
                        else:
                            intrasector_visited[output_cat_id] = True
                    
                    new_loss = node.outputs[output_cat_id].current_value * percentage
                    node.outputs[output_cat_id].current_value -= new_loss
                    elements.append((output_cat_id, new_loss))
        
        for sector in self.nodes:
            new_input = 0
            for input_sector in self.nodes:
                if sector in self.nodes[input_sector].outputs:
                    new_input += self.nodes[input_sector].outputs[sector].current_value
            self.nodes[sector].final_input_sum = new_input

    def print_graph(self):
        G = nx.Graph()
        visual = []

        for u in self.nodes:
            for v in self.nodes[u].outputs:
                visual.append([u, v])

        G.add_edges_from(visual)
        nx.draw_networkx(G)
        plt.show()

    def print_inputs(self):
        for id, node in self.nodes.items():
            perc = (node.initial_input_sum - node.final_input_sum) / node.initial_input_sum
            
            print(f"Node[{id}] perc {perc * 100} %, affected ({node.outputs.keys()})")

if __name__ == "__main__":
    graph = Graph()
    graph.load_data("data\\economics\\IONom\\processed\\NOMINAL_MAKE_2019.csv")
    graph.add_loss_impact("15", 150000)
    graph.print_graph()
    graph.print_inputs()


# Sector,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
# 1,19744.49388959431,0.0,61.650689044453436,358.2963416823181,
# 2,0.0,17317.747315157012,47.24475435532516,0.0,0.0,324.1257176596837