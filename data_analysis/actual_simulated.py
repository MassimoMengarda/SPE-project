import argparse
import os
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import math

from data_extraction_and_preprocessing.utils import get_dates_from_input_dir, read_csv

plt.style.use("seaborn-whitegrid")

def datetime_converter(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d")

def main(nyt_cases_file, no_countermeasure_dir, output_dir):
    dates_paths = get_dates_from_input_dir(no_countermeasure_dir, extension="")
    dates_paths.sort(key=lambda tup: tup[0])

    date_time = []
    simulated_cases = []
    total_cases = []
    ci = []

    nyt_cases = read_csv(nyt_cases_file, converters={"date": datetime_converter})
    cases = nyt_cases.groupby(["date"]).sum()
    
    for filename, dir_path in dates_paths:
        for i in range(168):
            if i % 24 != 0:
                continue
            current_datetime = datetime.datetime.strptime(filename.strip().strip('/'), '%Y-%m-%d') + datetime.timedelta(hours = i)
            date_time.append(current_datetime)
            
            results_standard = np.load(os.path.join(dir_path, f"{i:03}.npy"))
            
            sum_cases = np.sum(results_standard[4] + results_standard[3] + results_standard[2], axis=2)
            actual_cumulative_cases = np.mean(sum_cases)
            actual_ci = np.std(sum_cases)
            actual_ci = 1.959964 * (np.std(sum_cases) / math.sqrt(sum_cases.shape[0])) # 95 percentile
            # actual_ci = 2.575829 * (np.std(sum_cases) / math.sqrt(sum_cases.shape[0])) # 99 percentile
            
            ci.append(actual_ci)
            simulated_cases.append(actual_cumulative_cases)
            cases_datetime = current_datetime
            if cases_datetime in cases.index:
                total_cases.append(cases.loc[cases_datetime]["cases"])
            else:
                total_cases.append(0)

            print(f"Done {i}")
        print(f"Done {filename}")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ticker = matplotlib.ticker.EngFormatter(unit='')

    ax.set_title("Cumulative cases count (2020)")
    simulated_cases_np = np.asarray(simulated_cases)
    ax.plot(date_time, simulated_cases_np, label='Simulated')
    ax.plot(date_time, np.asarray(total_cases), label="Total")
    ax.fill_between(date_time, simulated_cases_np - np.asarray(ci), simulated_cases_np + np.asarray(ci), color='b', alpha=.1)
    ax.yaxis.set_major_formatter(ticker)
    ax.legend(frameon=False)
    ax.set_ylabel('People')
    ax.tick_params(axis='x', rotation=30)

    # axs[2].plot(x, np.asarray(removed_alive_countermeasure), label="Healed with")
    # axs[2].plot(x, np.asarray(removed_alive_standard), label="Healed without")

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot the actual cases vs the simulated cases")
    parser.add_argument("nyt_cases_file", type=str, help="the filepath to the NYT cases")
    parser.add_argument("no_countermeasure_dir", type=str, help="the directory where the no countermeasures simulation results are stored")
    parser.add_argument("output_dir", type=str, help="the directory where store the result")
    
    args = parser.parse_args()
    nyt_cases_file = args.nyt_cases_file
    no_countermeasure_dir = args.no_countermeasure_dir
    output_dir = args.output_dir
    
    main(nyt_cases_file, no_countermeasure_dir, output_dir)