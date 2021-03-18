import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def JSONParser(data):
    j1 = json.loads(data)
    return j1

def get_social_distancing_files_by_week(social_distancing_files):
    social_distancing_files_by_week = {}

    for filename, filepath in social_distancing_files:
        date_time = datetime.strptime(filename[:len("2019-01-08")], "%Y-%m-%d")
        start = date_time - timedelta(days=date_time.weekday())
        start_date_str = start.strftime("%Y-%m-%d")
        if start_date_str in social_distancing_files_by_week:
            social_distancing_files_by_week[start_date_str].append((date_time, filename, filepath))
        else:
            social_distancing_files_by_week[start_date_str] = [(date_time, filename, filepath)]
    
    for key in social_distancing_files_by_week:
        social_distancing_files_by_week[key] = sorted(social_distancing_files_by_week[key], key=lambda social_dist_file: social_dist_file[0])

    return social_distancing_files_by_week

def main():
    parser = argparse.ArgumentParser(description="Construct the h_ci(t) matrix, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the social distancing are stored")
    parser.add_argument("index_directory", type=str, help="the directory where the matrix index are stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    index_dir = args.index_directory
    output_dir = args.output_directory

    if not os.path.isdir(input_dir):
        print("Input directory is not a directory")
        sys.exit(1)
    
    cbg_idx_filename = os.path.join(index_dir, "cbg_indexes.csv")

    if not os.path.isfile(cbg_idx_filename):
        print("The given indexes directory do not contain the valid index file")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)

    cbg_idx_file = pd.read_csv(cbg_idx_filename)
    
    social_distancing_files = [(path, os.path.join(input_dir, path)) for path in os.listdir(input_dir) if path.endswith(".csv")]

    if len(social_distancing_files) == 0:
        print("Given input directory do not contain any CSV file") 
        sys.exit(1)

    social_distancing_files_by_week = get_social_distancing_files_by_week(social_distancing_files)

    for week in social_distancing_files_by_week:
        day_of_the_week = 0
        merged_df_set = False
        for date, filename, filepath in social_distancing_files_by_week[week]:
            print("Reading CSV file ", filepath)
            df = pd.read_csv(filepath)
            fraction_left_home = 1 - (df["completely_home_device_count"] / df["device_count"])

            df = pd.DataFrame({"cbg" : df["origin_census_block_group"], "fraction_left_home_" + str(day_of_the_week) : fraction_left_home})
            day_of_the_week += 1

            if merged_df_set:
                merged_df = pd.merge(merged_df, df, on="cbg", how="outer")
            else:
                merged_df_set = True
                merged_df = df
        
        ordered_df = pd.merge(cbg_idx_file, merged_df, on="cbg", how="left")

        for day in range(day_of_the_week):
            fraction_left_home_mean = ordered_df["fraction_left_home_" + str(day)].mean()
            ordered_df["fraction_left_home_" + str(day)].fillna(fraction_left_home_mean, inplace=True)

        flhs = []
        for day in range(day_of_the_week):
            flhs.append(ordered_df["fraction_left_home_" + str(day)].tolist())
        fhls_array = np.asarray(flhs, dtype=np.float32).T

        # print(fhls_array)
        
        output_filepath = os.path.join(output_dir, week)
        print("Writing file ", output_filepath)
        np.save(output_filepath, fhls_array)

if __name__ == "__main__":
    main()
