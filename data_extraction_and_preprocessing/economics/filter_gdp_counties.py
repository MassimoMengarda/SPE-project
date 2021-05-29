import argparse
import os

import numpy as np
import pandas as pd

from ..utils import read_csv

def main(gmp_county_filepath, county_list_filepath, output_filepath):
    gmp_county_file = read_csv(gmp_county_filepath)
    counties_file = read_csv(county_list_filepath)
    
    mask = np.full((len(gmp_county_file),), False)
    for idx, gmp_county in gmp_county_file.iterrows():
        for _, counties in counties_file.iterrows():
            gmp_county["county"] == counties[""]
            if 
            mask[idx] = True
    
    gmp_county_file = gmp_county_file[mask]
    
    
    
    
    categories = pd.Series(pd.unique(poi_categories_file["sub_category"]))
    categories_df = pd.DataFrame({"cat_name": categories, "lower_cat_name": categories.str.lower().str.strip()})
    
    categories_df = categories_df[~(pd.isna(categories_df["lower_cat_name"]))]
    
    naics_df = read_csv(naics_code_list_path, sep=";", converters={'code': str})
    naics_df["category"] = naics_df["category"].str.lower().str.strip()
    categories_with_naics_code_df = categories_df.merge(naics_df, left_on="lower_cat_name", right_on="category", how="left")
    # Add missing element
    categories_with_naics_code_df.loc[categories_with_naics_code_df["cat_name"].str.strip() == "Malls"] = ("Malls", "malls", "531120", "Lessors of Nonresidential Buildings (except Miniwarehouses)", "both")
    io_sector_list = []
    io_df = read_csv(naics_to_io_sector_path, sep=";", converters={'NAICS': str,'sector_number':int})
    for _, categories_with_naics_code_row in categories_with_naics_code_df.iterrows():
        naics_code = categories_with_naics_code_row["code"]
        is_best_fitting_set = False
        best_fitting = -1
        best_fitting_eq_chars = 0
        for _, io_df_row in io_df.iterrows():
            if io_df_row["NAICS"].strip() == "NA":
                continue
            
            io_naics_codes = [x.strip() for x in io_df_row["NAICS"].split(",")]
            for io_naics_code in io_naics_codes:
                if not is_best_fitting_set:
                    is_best_fitting_set = True
                    best_fitting = io_df_row["sector_number"]
                    best_fitting_eq_chars = equal_characters(naics_code, io_naics_code)
                    continue
                
                current_eq_char = equal_characters(naics_code, io_naics_code)
                if current_eq_char > best_fitting_eq_chars:
                    best_fitting_eq_chars = current_eq_char
                    best_fitting = io_df_row["sector_number"]
        io_sector_list.append(best_fitting)
    
    categories_with_io_df = categories_with_naics_code_df.join(pd.DataFrame({"io_sector": io_sector_list}))

    poi_categories_with_io_df = poi_categories_file.merge(categories_with_io_df, left_on="sub_category", right_on="cat_name", how="left")

    output_filepath = os.path.join(info_dir, "poi_categories_with_io_sector.csv")
    print("Writing file ", output_filepath)
    poi_categories_with_io_df.to_csv(output_filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter the GMP according to the list of counties in the simulation")
    parser.add_argument("gmp_county_filepath", type=str, help="the path to the file containing the gmp counties data")
    parser.add_argument("county_list_filepath", type=str, help="the path to the file containing the list of counties is stored")
    parser.add_argument("output_filepath", type=str, help="the path where to save the resul")
    
    args = parser.parse_args()
    gmp_county_filepath = args.gmp_county_filepath
    county_list_filepath = args.county_list_filepath
    output_filepath = args.output_filepath
    main(gmp_county_filepath, county_list_filepath, output_filepath)
