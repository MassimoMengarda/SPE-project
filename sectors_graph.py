import argparse
import sys
from argparse import ArgumentError

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from data_extraction_and_preprocessing.utils import read_csv


# TODO: inverse how the class work
class Node:
    def __init__(self, category_id):
        self.category_id = category_id
        self.inputs = {}
        self.outputs = {}
    
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
        self.io_matrix_days = 365

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
    def load_data(self, io_filepath, io_matrix_days=365):
        self.io_matrix_days = io_matrix_days
        io_df = read_csv(io_filepath, sep=",", index_col="Sector")

        for column in io_df:
            seller_idx = str(column).strip()
            self.nodes[seller_idx] = Node(seller_idx)

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
    
    def scale_sector_graph(self, simulation_start, simulation_end):
        simulation_duration = simulation_end - simulation_start
        print("simulation_duration.total_seconds() // 3600: ", simulation_duration.total_seconds() // 3600)
        print("(self.io_matrix_days * 24): ", (self.io_matrix_days * 24))
        scale_factor = (simulation_duration.total_seconds() // 3600) / (self.io_matrix_days * 24)
        print("scale_factor: ", scale_factor)
        for buyer_idx in self.nodes:
            for seller_idx in self.nodes[buyer_idx].inputs:
                self.nodes[buyer_idx].inputs[seller_idx].initial_exchange_total *= scale_factor
                self.nodes[buyer_idx].inputs[seller_idx].current_value *= scale_factor
                self.nodes[buyer_idx].inputs[seller_idx].loss *= scale_factor
    
    def add_loss_to_edge(self, supplier_sector, input_loss, buyer_sector=206): # 206 is final demand
        supplier_sector = str(supplier_sector)
        buyer_sector = str(buyer_sector)

        assert(input_loss <= self.nodes[supplier_sector].outputs[buyer_sector].current_value, "Input loss must be lower than the final demand")
        
        message_list = [(supplier_sector, input_loss)]
        self.nodes[supplier_sector].outputs[buyer_sector].current_value -= input_loss

        while len(message_list) > 0:
            message_supplier_sector, message_input_loss = message_list.pop(0)
            node = self.nodes[message_supplier_sector]
            
            output_sum = node.get_current_output_sum()
            loss_percentage = message_input_loss / output_sum if output_sum != 0 else 0
            
            assert(loss_percentage <= 1, "Percentage greater than 1")
            assert(loss_percentage >= 0, "Percentage smaller than 0")

            if loss_percentage > self.delta: # if the percentage is irrelevant, do not compute the changes
                for input_cat_id in node.inputs:
                    node.inputs[input_cat_id].current_value *= (1 - loss_percentage)
                    message_list.append((input_cat_id, loss_percentage))
    
    def get_edge_initial_exchange_total(self, supplier_sector, buyer_sector="206"):
        supplier_sector = str(supplier_sector)
        buyer_sector = str(buyer_sector)
        if buyer_sector in self.nodes:
            if supplier_sector in self.nodes[buyer_sector].inputs:
                return self.nodes[buyer_sector].inputs[supplier_sector].initial_exchange_total
            
            raise ArgumentError(supplier_sector, f"No edge between {buyer_sector} and {supplier_sector}")
        raise ArgumentError(buyer_sector, f"No edge between {buyer_sector} and {supplier_sector}")

    def print_graph(self):
        G = nx.Graph()
        visual = []

        for u in self.nodes:
            for v in self.nodes[u].outputs:
                visual.append([u, v])

        G.add_edges_from(visual)
        nx.draw_networkx(G)
        plt.show()
    
    def save_sectors_graph(self, filepath):
        graph_to_save = np.zeros((3, len(self.nodes)), dtype=np.int64)
        node_idx = 0
        for node_id, node in self.nodes.items():
            graph_to_save[0, node_idx] = node_id
            graph_to_save[1, node_idx] = node.get_initial_output_sum()
            graph_to_save[2, node_idx] = node.get_current_output_sum()
            node_idx += 1
        np.save(filepath, graph_to_save)

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
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("io_filepath", type=str, help="the filepath to the IO tables")

    args = parser.parse_args()

    graph = Graph()
    graph.load_data(args.io_filepath)
    graph.add_loss_to_edge("168", 10000)
    graph.print_inputs()
    graph.print_graph()
