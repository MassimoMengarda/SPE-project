import scipy
from data_extraction_and_preprocessing.utils import read_npy, read_npz
from ipfn import ipfn
import numpy as np

def main():
    
    target = read_npz('/home/matteo/uniTN/simulation_performance/project-data/aggregate/aggregate_visit_matrix.npz').todense()
    cbg_marginals = read_npy('/home/matteo/uniTN/simulation_performance/project-data/cbg_marginals/2020-03-02.npy')[:,0]
    poi_marginals = read_npz('/home/matteo/uniTN/simulation_performance/project-data/poi_marginals/2020-03-02.npz').todense()[:,0]
    
    aggregates = [poi_marginals, cbg_marginals]
    dimensions = [[0], [1]]

    IPF = ipfn.ipfn(target, aggregates, dimensions)
    print("Iterations start")
    target = IPF.iteration()
    print("Iterations stop")
   
    print(target.shape)
    print(target)

if __name__ == "__main__":
    main()