import argparse
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from utils import get_dates_from_input_dir, read_csv

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

def main(input_dir, info_dir, output_dir):
    cbg_idx_file = read_csv(os.path.join(info_dir, "cbg_indexes.csv"))
    social_distancing_files = get_dates_from_input_dir(input_dir)
    social_distancing_files_by_week = get_social_distancing_files_by_week(social_distancing_files)
    os.makedirs(output_dir, exist_ok=True)

    for week in social_distancing_files_by_week:
        day_of_the_week = 0
        merged_df_set = False
        for date, filename, filepath in social_distancing_files_by_week[week]:
            df = read_csv(filepath)
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

        output_filepath = os.path.join(output_dir, week)
        print("Writing file ", output_filepath)
        np.save(output_filepath, fhls_array)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construct the h_ci(t) matrix, one for each week considered")
    parser.add_argument("input_directory", type=str, help="the directory where the social distancing are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the cbg index matrix is stored")
    parser.add_argument("output_directory", type=str, help="the directory where save the matrixes elaborated")
    args = parser.parse_args()
    input_dir = args.input_directory
    info_dir = args.info_directory
    output_dir = args.output_directory

    main(input_dir, info_dir, output_dir)
