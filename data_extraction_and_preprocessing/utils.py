import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
# https://pypi.org/project/pyshp/
import shapefile
from scipy.sparse import load_npz


def get_dates_from_input_dir(input_dir, extension=".csv"):
    result = []
    
    if not os.path.isdir(input_dir):
        sys.exit(f"{input_dir} is not a directory")

    for filename in os.listdir(input_dir):
        if filename.endswith(extension):
            try:
                filename_date = datetime.strptime(filename[:len("2019-01-08")], "%Y-%m-%d")
                new_filename = filename_date.strftime("%Y-%m-%d") + extension
                result.append((new_filename, os.path.join(input_dir, filename)))
            except ValueError as err:
                print(f"{filename} will be skipped - Wrong name format")

    if len(result) == 0:
        sys.exit(f"{input_dir} does not contain any {extension} files")

    return result

def JSONParser(data):
    return json.loads(data)

def read_csv(filepath, converters=None):
    if not os.path.isfile(filepath):
        sys.exit(f"{filepath} is not a valid CSV file")
    print("Reading CSV file", filepath)
    return pd.read_csv(filepath, converters=converters)

def read_npy(filepath):
    if not os.path.isfile(filepath):
        sys.exit(f"{filepath} is not a valid NPY file")
    print("Reading NPY file", filepath)
    return np.load(filepath)

def read_npz(filepath):
    if not os.path.isfile(filepath):
        sys.exit(f"{filepath} is not a valid NPZ file")
    print("Reading NPZ file", filepath)
    return load_npz(filepath)

def read_shapefile(filepath):
    if not os.path.isfile(filepath):
        sys.exit(f"{filepath} is not a valid shape file")
    print("Reading shape file", filepath)
    return shapefile.Reader(filepath)