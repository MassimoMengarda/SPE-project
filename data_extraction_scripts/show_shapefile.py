# https://pypi.org/project/pyshp/
import os
import sys

# pip3 install Polygon3
import Polygon
import shapefile
from shapely.geometry import Polygon

state_cbg_files = ["tl_2020_34_bg", "tl_2020_36_bg", "tl_2020_42_bg"]
dir_data = "data/additional_data/"

zcta = shapefile.Reader("data/additional_data/tl_2020_us_zcta510/tl_2020_us_zcta510")
zcta_records = zcta.records()

zip_bind = []
cbg_bind = []

for state_directory in state_cbg_files:
    dirpath = os.path.join(dir_data, state_directory)
    assert(os.path.isdir(dirpath) == True)
    cbg_sf = shapefile.Reader(os.path.join(dirpath, state_directory))
    cbg_sf_records = cbg_sf.records()
    print(cbg_sf.fields)
    for i, cbg_shape in enumerate(cbg_sf.shapes()):
        cbg_polygon = Polygon.Polygon(cbg_shape.points)
        cbg_code = cbg_sf_records[i][0]
        for j, zip_shape in enumerate(zcta.shapes()):
            zip_polygon = Polygon.Polygon(zip_shape.points)
            if (cbg_polygon & zip_polygon).area() > sys.float_info.epsilon:
                zip_code = zcta_records[j][0]
                zip_bind.append(zip_code)
                cbg_bind.append(cbg_code)
        #     x = zip_polygon.intersection(cbg_polygon)
