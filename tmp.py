import numpy as np
import torch

from data_extraction_and_preprocessing.utils import read_npy, read_npz, read_csv
from data_extraction_and_preprocessing.sparse_vector_utils import sparse_dense_vector_mul

def main():
    w_ij = torch.load('/storage/project-data/ipfp/2019-02-04/012.pth').cuda().coalesce()
    poi_categories = read_csv("/storage/project-data/matrix_info/poi_categories_with_io_sector.csv")
    cbg_population = read_npy("/storage/project-data/matrix_info/cbg_population_matrix.npy")

    poi_categories = torch.from_numpy(poi_categories["io_sector"].to_numpy()).cuda()
    poi_indeces = read_csv("/storage/project-data/matrix_info/poi_indexes.csv")

    food_categories = [168]
    
    people_inside_activity_in_hour = 0

    # Algorithm
    mask = torch.zeros_like(poi_categories, dtype=torch.bool, device='cuda')
    for food_category in food_categories:
        mask = torch.logical_or(mask, poi_categories == food_category)
        
    people_inside_poi = torch.sparse.sum(w_ij, dim=1).to_dense()
    people_inside_activity_in_hour = torch.sum(people_inside_poi[mask]).item()
    
    new_w_ij = sparse_dense_vector_mul(w_ij, torch.reshape(torch.logical_not(mask), (mask.shape[0], 1)))

    new_people_inside_poi = torch.sparse.sum(new_w_ij, dim=1).to_dense()
    new_people_inside_activity_in_hour = torch.sum(new_people_inside_poi[mask]).item()

    print("Before closure:", people_inside_activity_in_hour)
    print("After closure:", new_people_inside_activity_in_hour)

    print("All visits:", torch.sparse.sum(torch.sparse.sum(w_ij, dim=1)))
    print("All visits:", torch.sparse.sum(torch.sparse.sum(new_w_ij, dim=1)))

if __name__ == "__main__":
    main()