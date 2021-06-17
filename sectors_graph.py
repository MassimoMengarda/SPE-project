from typing import final

from numpy.lib.function_base import percentile
from data_extraction_and_preprocessing.utils import read_csv
import networkx as nx
import matplotlib.pyplot as plt
import sys

# TODO: inverse how the class work
class Node:
    def __init__(self, category_id, initial_output_sum):
        self.category_id = category_id
        self.inputs = {}
        self.outputs = {}
        
        self.final_output_sum = 0
        self.initial_output_sum = initial_output_sum
        self.current_output_sum = initial_output_sum
    
    def add_input_connection(self, key, value):
        if not key in self.inputs:
            self.inputs[key] = value
        else:
            print(f"WARNING: input {key} already present")
    
    def add_output_connection(self, key, value):
        if not key in self.outputs:
            self.outputs[key] = value
        else:
            print(f"WARNING: output {key} already present")

    def get_current_output_sum(self):
        current_output_sum = 0
        for output in self.outputs.values():
            current_output_sum += output.current_value
        return current_output_sum
    
    def get_initial_output_sum(self):
        initial_output_sum = 0
        for output in self.outputs.values():
            initial_output_sum += output.initial_exchange_total
        return initial_output_sum

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

    """
    Each column sums to its respective industry output => Output
    Each row sums to its respective commodity output => Input
    """
    # Iterate over rows
    # def load_data(self, io_filepath):
    #     io_df = read_csv(io_filepath, sep=",", index_col="Sector", converters={"Sector": lambda x : str(x).strip()})

    #     for idx, io_row in io_df.iterrows():
    #         clean_idx = str(idx).strip()
    #         inputs = {}

    #         if clean_idx == "206": # Skip value added
    #                 continue

    #         for output_category, value in io_row.iteritems():
    #             clean_output_category = str(output_category).strip()

    #             if value > sys.float_info.epsilon:
    #                 inputs[clean_output_category] = Edge(value, clean_output_category == clean_idx)
            
    #         self.nodes[clean_idx] = Node(clean_idx, inputs, io_df[clean_idx].sum())
    
    # Iterate over columns
    def load_data(self, io_filepath):
        io_df = read_csv(io_filepath, sep=",", index_col="Sector")

        for column in io_df:
            seller_idx = str(column).strip()
            self.nodes[seller_idx] = Node(seller_idx, io_df[column].sum() - io_df[column][206])

        for column in io_df:
            buyer_idx = str(column).strip()
            
            for idx, io_row in io_df.iterrows():
                seller_idx = str(idx).strip()

                if seller_idx == "206": # Skip value added
                    continue

                value = int(io_df[column][idx] * 1000000) # The IO table is represented as 1M dollars
                if value > sys.float_info.epsilon:
                    edge = Edge(value, seller_idx == buyer_idx)
                
                    self.nodes[seller_idx].add_output_connection(buyer_idx, edge)
                    self.nodes[buyer_idx].add_input_connection(seller_idx, edge)
    
    """
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
            new_output = 0
            for output_sector in self.nodes:
                if sector in self.nodes[output_sector].outputs:
                    new_output += self.nodes[output_sector].outputs[sector].current_value
            self.nodes[sector].final_output_sum = new_output
    """
    
    # add_loss_to_edge(5, 5000)
    def add_loss_to_edge(self, supplier_sector, input_loss, buyer_sector="206"): # 206 is final demand
        assert(input_loss <= self.nodes[supplier_sector].outputs[buyer_sector].current_value, "Input loss must be lower than the final demand")
        message_list = [(supplier_sector, input_loss)]
        self.nodes[supplier_sector].outputs[buyer_sector].current_value -= input_loss

        while len(message_list) > 0:
            message_supplier_sector, message_input_loss = message_list.pop(0)
            node = self.nodes[message_supplier_sector]
            
            output_sum = node.get_current_output_sum()
            loss_percentage = message_input_loss / output_sum
            
            assert(loss_percentage <= 1, "Percentage greater than 1")
            assert(loss_percentage >= 0, "Percentage smaller than 0")

            if loss_percentage > self.delta: # if the percentage is irrelevant, do not compute the changes
                for input_cat_id in node.inputs:
                    node.inputs[input_cat_id].current_value *= (1 - loss_percentage)
                    message_list.append((input_cat_id, loss_percentage))
    
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
            initial_output_sum = node.get_initial_output_sum()
            current_output_sum = node.get_current_output_sum()
            
            if initial_output_sum > sys.float_info.epsilon:
                perc = (initial_output_sum - current_output_sum) / initial_output_sum
            else:
                perc = 0.0
            
            # print(f"Node[{id}] Initial sum {initial_output_sum}")
            # print(f"Node[{id}] Final sum {current_output_sum}")
            print(f"Node[{id}] perc loss {perc * 100} %")#, affected ({node.outputs.keys()})")

    def get_total_economic_loss(self):
        initial_total = 0
        final_total = 0

        for node in self.nodes.values():
            initial_total += node.get_initial_output_sum()
            final_total += node.get_current_output_sum()

        percentage = (initial_total - final_total) / initial_total

        return {
            "loss": initial_total - final_total,
            "percentage": percentage
        }

if __name__ == "__main__":
    graph = Graph()
    graph.load_data("data\\economics\\IONom\\processed\\NOMINAL_USE_2019.csv")
    graph.add_loss_to_edge("15", 80000)
    graph.add_loss_to_edge("15", 10000)
    graph.print_inputs()
    graph.print_graph()
