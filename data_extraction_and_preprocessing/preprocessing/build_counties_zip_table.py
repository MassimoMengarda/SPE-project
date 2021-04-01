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
    zcta = read_shapefile(os.path.join(input_dir, "zcta", "tl_2020_us_zcta510"))
    counties = read_shapefile(os.path.join(input_dir, "counties", "cb_2019_us_county_500k"))
    zip_in_metro_df = read_csv(zip_in_metro_area_filepath, converters={"zip_code": str})
    
    counties_records = counties.records()
    counties_shapes = counties.shapes()

    counties_polygons = []
    zip_bind = []
    counties_bind = {
        'state_fp': [],
        'county_fp': [],
        'county_ns': [],
        'aff_geoid': [],
        'geoid': [],
        'name': [],
        'lsad': []
    }
    bar = Bar("Polygons creation", max=len(counties_shapes))
    for zip_shape in counties_shapes:
        counties_polygons.append(Polygon.Polygon(zip_shape.points))
        bar.next()
    bar.finish()

    counties_idx = index.Index()
    bar = Bar("Index creation", max=len(counties_polygons))
    for pos, cell in enumerate(counties_polygons):
        bb = cell.boundingBox()
        if bb[0] > bb[2]:
            bb = (bb[2], bb[1], bb[0], bb[3])
        if bb[1] > bb[3]:
            bb = (bb[0], bb[3], bb[2], bb[1])
        counties_idx.insert(pos, bb)
        bar.next()
    bar.finish()

    zcta_sf_records = zcta.records()
    zcta_sf_shapes = zcta.shapes()
    total_length = len(zcta_sf_shapes)
    
    
    bar = Bar("ZCTA bind", max=total_length)
    for i, zcta_shape in enumerate(zcta_sf_shapes):
        zcta_polygon = Polygon.Polygon(zcta_shape.points)
        zcta_code = zcta_sf_records[i][0]
        zcta_bb = zcta_polygon.boundingBox()
        if zcta_bb[0] > zcta_bb[2]:
            zcta_bb = (zcta_bb[2], zcta_bb[1], zcta_bb[0], zcta_bb[3])
        if zcta_bb[1] > zcta_bb[3]:
            zcta_bb = (zcta_bb[0], zcta_bb[3], zcta_bb[2], zcta_bb[1])
        for pos in counties_idx.intersection(zcta_bb):
            if zcta_polygon.overlaps(counties_polygons[pos]):
                zip_bind.append(zcta_code)
                counties_bind['state_fp'].append(counties_records[pos][0])
                counties_bind['county_fp'].append(counties_records[pos][1])
                counties_bind['county_ns'].append(counties_records[pos][2])
                counties_bind['aff_geoid'].append(counties_records[pos][3])
                counties_bind['geoid'].append(counties_records[pos][4])
                counties_bind['name'].append(counties_records[pos][5])
                counties_bind['lsad'].append(counties_records[pos][6])
        bar.next()
    bar.finish()
    
    out_df = pd.DataFrame(data=dict({"zip": zip_bind}, **counties_bind))
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
