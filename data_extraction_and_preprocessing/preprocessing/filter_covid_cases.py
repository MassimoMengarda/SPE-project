import argparse
import sys
import os

import pandas as pd

from ..utils import read_csv

def main(ny_times_cases_filepath, zip_counties_filepath, output_filepath):
    nyt_covid_df = read_csv(ny_times_cases_filepath, converters={"fips": str})
    zip_counties_df = read_csv(zip_counties_filepath, converters={"zip": str, "geoid": str})

    is_metro_area = nyt_covid_df["fips"].isin(zip_counties_df["geoid"])
    nyt_covid_df = nyt_covid_df[is_metro_area]

    nyt_covid_df = nyt_covid_df[nyt_covid_df['state'] != 'Pennsylvania']
    # print(nyt_covid_df[nyt_covid_df['state'] == 'Pennsylvania']['county'].value_counts())
    
    print(f"Saving CSV file {output_filepath}")
    nyt_covid_df.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter all population files by zip codes")
    parser.add_argument("ny_times_cases_filepath", type=str, help="the number of cases, as exposed inside the NY times COVID-19 dataset (us-counties.csv)")
    parser.add_argument("zip_counties_filepath", type=str, help="the path to where zip cbg file is stored")
    parser.add_argument("output_filepath", type=str, help="the path where to save the results")
    args = parser.parse_args()
    ny_times_cases_filepath = args.ny_times_cases_filepath
    zip_counties_filepath = args.zip_counties_filepath
    output_filepath = args.output_filepath

    main(ny_times_cases_filepath, zip_counties_filepath, output_filepath)
