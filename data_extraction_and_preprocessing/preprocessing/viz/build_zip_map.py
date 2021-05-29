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

def main(input_dir, zip_in_metro_area_filepath, output_filepath):
    gp = geopandas.read_file(os.path.join(input_dir, "zcta", "tl_2020_us_zcta510.shp"))
    zip_in_metro_df = read_csv(zip_in_metro_area_filepath, converters={"zip_code": str})
    
    is_metro_area = gp["ZCTA5CE10"].isin(zip_in_metro_df["zip_code"])
    print(gp[is_metro_area])
    gp[is_metro_area].plot()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the cbg zip table")
    parser.add_argument("input_directory", type=str, help="the directory where the shape files are stored")
    parser.add_argument("zip_in_metro_area_filepath", type=str, help="the path to the zip in metro area file")
    parser.add_argument("output_filepath", type=str, help="the file path where to save the result")
    args = parser.parse_args()
    input_dir = args.input_directory
    zip_in_metro_area_filepath = args.zip_in_metro_area_filepath
    output_filepath = args.output_filepath

    main(input_dir, zip_in_metro_area_filepath, output_filepath)