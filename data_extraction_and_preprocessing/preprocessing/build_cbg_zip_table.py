import argparse
import os
import sys

import pandas as pd
# pip3 install Polygon3
import Polygon
from progress.bar import Bar
from rtree import index

from ..utils import read_shapefile, read_csv

def main(input_dir, zip_in_metro_area_filepath, output_filepath):
    state_cbg_files = ["tl_2020_34_bg", "tl_2020_36_bg", "tl_2020_42_bg"]
    zcta = read_shapefile(os.path.join(input_dir, "zcta", "tl_2020_us_zcta510"))
    zip_in_metro_df = read_csv(zip_in_metro_area_filepath, converters={"zip_code": str})

    zcta_records = zcta.records()
    zcta_shapes = zcta.shapes()

    zcta_polygons = []
    zip_bind = []
    cbg_bind = []
    bar = Bar("Polygons creation", max=len(zcta_shapes))
    for zip_shape in zcta_shapes:
        zcta_polygons.append(Polygon.Polygon(zip_shape.points))
        bar.next()
    bar.finish()

    zcta_idx = index.Index()
    bar = Bar("Index creation", max=len(zcta_polygons))
    for pos, cell in enumerate(zcta_polygons):
        bb = cell.boundingBox()
        if bb[0] > bb[2]:
            bb = (bb[2], bb[3], bb[0], bb[1])
        zcta_idx.insert(pos, bb)
        bar.next()
    bar.finish()

    for state_directory in state_cbg_files:
        cbg_sf = read_shapefile(os.path.join(input_dir, "state_cbgs", state_directory, state_directory))
        cbg_sf_records = cbg_sf.records()
        cbg_sf_shapes = cbg_sf.shapes()
        total_length = len(cbg_sf_shapes)
        
        bar = Bar(state_directory, max=total_length)
        for i, cbg_shape in enumerate(cbg_sf_shapes):
            cbg_polygon = Polygon.Polygon(cbg_shape.points)
            cbg_code = cbg_sf_records[i][4]
            for pos in zcta_idx.intersection(cbg_polygon.boundingBox()):
                if cbg_polygon.overlaps(zcta_polygons[pos]):
                    zip_code = zcta_records[pos][0]
                    zip_bind.append(zip_code)
                    cbg_bind.append(cbg_code)
            bar.next()
        bar.finish()

    out_df = pd.DataFrame(data={"zip": zip_bind, "cbg": cbg_bind})
    out_df.drop_duplicates(inplace=True)

    print("Filtering data")
    is_metro_area = out_df["zip"].isin(zip_in_metro_df["zip_code"])
    final_df = out_df[is_metro_area]

    final_df.to_csv(output_filepath, index=False)

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
