import argparse
import os

import numpy as np
import pandas as pd

from ..utils import read_csv

def equal_characters(str1, str2):
    eq_char = 0
    i = 0
    while i < min(len(str1), len(str2)):
        if str1[i] == str2[i]:
            eq_char += 1
        else:
            break
        i += 1
    return eq_char

def main(info_dir, naics_code_list_path, naics_to_io_sector_path):
    poi_categories_file = read_csv(os.path.join(info_dir, "poi_categories.csv"))
    categories = pd.Series(pd.unique(poi_categories_file["sub_category"]))
    categories_df = pd.DataFrame({"cat_name": categories, "lower_cat_name": categories.str.lower().str.strip()})
    
    categories_df = categories_df[~(pd.isna(categories_df["lower_cat_name"]))]
    
    naics_df = read_csv(naics_code_list_path, sep=";", converters={'code': str})
    naics_df["category"] = naics_df["category"].str.lower().str.strip()
    categories_with_naics_code_df = categories_df.merge(naics_df, left_on="lower_cat_name", right_on="category", how="left")

    # Add missing element
    mask = categories_with_naics_code_df["cat_name"].str.strip() == "Malls"
    categories_with_naics_code_df.loc[mask] = ("Malls", "malls", "531120", "Lessors of Nonresidential Buildings (except Miniwarehouses)")

    io_sector_list = []
    io_df = read_csv(naics_to_io_sector_path, sep=";", converters={'NAICS': str, 'sector_number':int})

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
    print("Writing file", output_filepath)
    poi_categories_with_io_df["io_sector"] = poi_categories_with_io_df["io_sector"].fillna(0)
    poi_categories_with_io_df["io_sector"] = poi_categories_with_io_df["io_sector"].astype(int)

    poi_categories_with_io_df[["matrix_idx", "io_sector"]].to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the IO matrixes strating from POI categories and NAICS codes")
    parser.add_argument("info_directory", type=str, help="the directory where the poi categories file is stored")
    parser.add_argument("naics_code_list_path", type=str, help="the path to the file containing the list of NAICS codes")
    parser.add_argument("naics_to_io_sector_path", type=str, help="the path to the file containing the binding between IO sectors and NAICS codes")
    
    args = parser.parse_args()
    info_dir = args.info_directory
    naics_code_list_path = args.naics_code_list_path
    naics_to_io_sector_path = args.naics_to_io_sector_path
    main(info_dir, naics_code_list_path, naics_to_io_sector_path)
