import geopandas

import argparse
import os

import pandas as pd
# pip3 install Polygon3

from ...utils import read_shapefile, read_csv

import matplotlib.pyplot as plt

def main(input_dir, zip_cbg_filepath):
    state_cbg_files = ["tl_2020_34_bg", "tl_2020_36_bg", "tl_2020_42_bg"]

    paths = []
    for state_directory in state_cbg_files:
        paths.append(os.path.join(input_dir, "state_cbgs", state_directory, state_directory + ".shp"))

    states_cbg_df = geopandas.GeoDataFrame(pd.concat([geopandas.read_file(i) for i in paths], ignore_index=True), crs=geopandas.read_file(paths[0]).crs)
    
    zip_cbg_df = read_csv(zip_cbg_filepath, converters={'cbg':str,'zip':str})
    cbg_list = pd.unique(zip_cbg_df["cbg"])
    print(cbg_list)
    print("length cbg_list: ", len(cbg_list))
    print(states_cbg_df)

    is_metro_area = states_cbg_df["GEOID"].isin(cbg_list)
    print(states_cbg_df[is_metro_area])
    
    states_cbg_df[is_metro_area].plot()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg zip table")
    parser.add_argument("input_directory", type=str, help="the directory where the shape files are stored")
    parser.add_argument("zip_cbg_filepath", type=str, help="the directory where the zip cbg file is stored")
    # parser.add_argument("zip_in_metro_area_filepath", type=str, help="the path to the zip in metro area file")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_cbg_filepath = args.zip_cbg_filepath
    # zip_in_metro_area_filepath = args.zip_in_metro_area_filepath

    main(input_dir, zip_cbg_filepath)