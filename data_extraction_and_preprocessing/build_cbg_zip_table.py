import os
import sys

# pip3 install Polygon3
import Polygon
# https://pypi.org/project/pyshp/
import shapefile
from rtree import index
import pandas as pd
from progress.bar import Bar

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: PATH/python3 build_cbg_zip_table.py <dir data> <output filepath>")
    
    dir_data = sys.argv[1]
    output_filepath = sys.argv[2]

    state_cbg_files = ["tl_2020_34_bg", "tl_2020_36_bg", "tl_2020_42_bg"]

    zcta_input_file = os.path.join(dir_data, "zcta", "tl_2020_us_zcta510")
    print("Reading zcta input file {}".format(zcta_input_file))
    zcta = shapefile.Reader(zcta_input_file)
    zcta_records = zcta.records()

    print(zcta.fields)
    print(zcta_records[0])

    zip_bind = []
    cbg_bind = []

    zcta_shapes = zcta.shapes()
    zcta_polygons = []
    bar = Bar('Polygons creation', max=len(zcta_shapes))
    for j, zip_shape in enumerate(zcta_shapes):
        zcta_polygons.append(Polygon.Polygon(zip_shape.points))
        bar.next()
    bar.finish()
    zcta_idx = index.Index()
    bar = Bar('Index creation', max=len(zcta_polygons))
    for pos, cell in enumerate(zcta_polygons):
        bb = cell.boundingBox()
        if bb[0] > bb[2]:
            bb = (bb[2], bb[3], bb[0], bb[1])
        zcta_idx.insert(pos, bb)
        bar.next()
    bar.finish()

    for state_directory in state_cbg_files:
        dirpath = os.path.join(dir_data, "state_cbgs", state_directory)
        print(dirpath)
        assert(os.path.isdir(dirpath) == True)
        cbg_sf = shapefile.Reader(os.path.join(dirpath, state_directory))
        cbg_sf_records = cbg_sf.records()
        print(cbg_sf.fields)
        print(cbg_sf_records[0])
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
    # print(zip_bind)
    # print(cbg_bind)
    out_df = pd.DataFrame(data={'zip':zip_bind,'cbg':cbg_bind})
    out_df.drop_duplicates(inplace=True)
    out_df.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    main()
