import geopandas

import argparse
import os
import sys

import pandas as pd
# pip3 install Polygon3
import Polygon
from progress.bar import Bar
from rtree import index

from ...utils import read_shapefile, read_csv

import matplotlib.pyplot as plt

def main(input_dir):
    state_cbg_files = ["tl_2020_34_bg", "tl_2020_36_bg", "tl_2020_42_bg"]

    paths = []
    for state_directory in state_cbg_files:
        paths.append(os.path.join(input_dir, "state_cbgs", state_directory, state_directory + ".shp"))

    states_cbg_df = geopandas.GeoDataFrame(pd.concat([geopandas.read_file(i) for i in paths], ignore_index=True), crs=geopandas.read_file(paths[0]).crs)
    
    print(states_cbg_df)
    
    states_cbg_df.plot()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg zip table")
    parser.add_argument("input_directory", type=str, help="the directory where the shape files are stored")
    # parser.add_argument("zip_in_metro_area_filepath", type=str, help="the path to the zip in metro area file")
    args = parser.parse_args()
    input_dir = args.input_directory
    # zip_in_metro_area_filepath = args.zip_in_metro_area_filepath

    main(input_dir)