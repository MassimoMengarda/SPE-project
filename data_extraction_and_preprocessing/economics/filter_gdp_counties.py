import argparse
import json

import numpy as np

from ..utils import read_csv

def main(gmp_county_filepath, county_list_filepath, output_filepath):
    gmp_county_file = read_csv(gmp_county_filepath)
    counties_file = read_csv(county_list_filepath)
    
    print("Computing NY area counties")
    mask = np.full((len(gmp_county_file),), False)
    for idx, gmp_county in gmp_county_file.iterrows():
        for _, counties in counties_file.iterrows():
            if gmp_county["county"].strip().lower() == counties["name"].strip().lower():
                mask[idx] = True
    
    gmp_county_file_clean = gmp_county_file[mask]

    total_gdp = gmp_county_file[gmp_county_file["county"] == "United States"].loc[0]["gdp_2019"]
    ny_are_gdp = gmp_county_file_clean["gdp_2019"].sum()

    print(total_gdp)
    print(ny_are_gdp)

    scale_factor = ny_are_gdp / total_gdp

    print(scale_factor)

    print("Writing JSON ", output_filepath)
    with open(output_filepath, 'w') as fhandle:
        json.dump({"metro_area_scale_factor" : scale_factor}, fhandle)
    
    # gmp_county_file_clean.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter the GMP according to the list of counties in the simulation")
    parser.add_argument("gmp_county_filepath", type=str, help="the path to the file containing the gmp counties data")
    parser.add_argument("county_list_filepath", type=str, help="the path to the file containing the list of counties is stored")
    parser.add_argument("output_filepath", type=str, help="the path where to save the results as json")
    
    args = parser.parse_args()
    gmp_county_filepath = args.gmp_county_filepath
    county_list_filepath = args.county_list_filepath
    output_filepath = args.output_filepath
    main(gmp_county_filepath, county_list_filepath, output_filepath)
