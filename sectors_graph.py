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
        self.current_input_sum = initial_input_sum

class Edge:
    def __init__(self, initial_exchange_total, intrasector):
        self.initial_exchange_total = initial_exchange_total
        self.current_value = initial_exchange_total
        self.loss = 0.0
        self.intrasector = intrasector

class Graph:
    def __init__(self, delta=0.001):
        self.nodes = {}
        self.delta = delta
    
    # Iterate over rows
    def load_data(self, io_filepath):
        io_df = read_csv(io_filepath, sep=",", index_col="Sector", converters={"Sector": lambda x : str(x).strip()})
        # io_df = io_df.transpose()

        for idx, io_row in io_df.iterrows():
            idx = str(idx).strip()
            outputs = {}

            for output_category, value in io_row.iteritems():
                output_category_strip = str(output_category).strip()
                if value > sys.float_info.epsilon:
                    outputs[output_category_strip] = Edge(value, output_category_strip == idx)
            
            self.nodes[idx] = Node(idx, outputs, io_df[idx].sum())
            # self.nodes[idx] = Node(idx, outputs, io_df[int(idx)].sum())
    
    # # Iterate over columns
    # def load_data(self, io_filepath):
    #     io_df = read_csv(io_filepath, sep=",", index_col="Sector")
    #     for column in io_df:
    #         category_idx = str(column).strip()
    #         outputs = {}
            
    #         for idx, io_row in io_df.iterrows():
    #             value = io_df[column][idx]
    #             if value > sys.float_info.epsilon:
    #                 outputs[str(idx).strip()] = Edge(value, category_idx == idx)
            
    #         self.nodes[category_idx] = Node(category_idx, outputs, io_df[column].sum())
    
    def add_loss_impact(self, input_sector, input_loss): # peso effettivo in entrata
        assert(input_loss <= self.nodes[input_sector].initial_input_sum)
        elements = [(input_sector, input_loss)]
        
        while len(elements) > 0:
            sector, loss = elements.pop(0)
            node = self.nodes[sector]
            percentage = loss / node.initial_input_sum

            if percentage > self.delta: # if the percentage is irrelevant, do not compute the changes
                for output_cat_id in node.outputs:
                    output_loss = node.outputs[output_cat_id].current_value * percentage
                    node.outputs[output_cat_id].current_value -= output_loss
                    # self.nodes[output_cat_id].current_input_sum -= output_loss
                    # print(f"From {sector} to {output_cat_id} loss {output_loss}")
                    # print(f"From {sector} to {output_cat_id} current value {node.outputs[output_cat_id].current_value}")

                    elements.append((output_cat_id, output_loss))
        
        # Compute the final input sum
        for sector in self.nodes:
            new_input = 0
            for input_sector in self.nodes:
                if sector in self.nodes[input_sector].outputs:
                    new_input += self.nodes[input_sector].outputs[sector].current_value
            self.nodes[sector].final_input_sum = new_input
    
    def add_loss_to_edge(self):
        pass

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
            print(f"Node[{id}] perc loss {perc * 100} %")#, affected ({node.outputs.keys()})")

if __name__ == "__main__":
    graph = Graph()
    graph.load_data("data\\economics\\IONom\\processed\\NOMINAL_USE_2019.csv")
    # graph.load_data("data\\tmp\\fake_nom_use2.csv")
    graph.add_loss_impact("15", 15000)
    # graph.print_graph()
    graph.print_inputs()
