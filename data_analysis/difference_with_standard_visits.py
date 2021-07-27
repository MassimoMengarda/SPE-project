import argparse
import os
import datetime
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from torch.functional import split
import string

from data_extraction_and_preprocessing.utils import get_dates_from_input_dir

plt.style.use("seaborn-whitegrid")

def label_to_multiline(label : str) -> str:
    return ' '.join([x + ("\n" if (i + 1) % 3 == 0 else "") for i, x in enumerate(label.split(" "))])

def main(countermeasure_results_dirs, countermeasure_names):
    dates_paths = get_dates_from_input_dir(countermeasure_results_dirs[0], extension="")
    dates_paths.sort(key=lambda tup: tup[0])

    date_time = []
    visits_countermeasure = []
    for i in range(len(countermeasure_results_dirs)):
        visits_countermeasure.append([])
    
    
    for filename, dir_path in dates_paths:
        for i in range(7):
            date_time.append(datetime.datetime.strptime(filename.strip().strip('/'), '%Y-%m-%d') + datetime.timedelta(days = i))
            
            for e, countermeasure_dir in enumerate(countermeasure_results_dirs):
                daily_visits = 0
                for j in range(24):
                    visits_simulation_results_countermeasure = np.load(os.path.join(countermeasure_dir, filename, f"visit_diff_{i*24 + j:03}.npy"))
                    daily_visits += np.sum(visits_simulation_results_countermeasure)
                visits_countermeasure[e].append(daily_visits)
                print(f"Done {i*24 + j}")
        print(f"Done {filename}")

    ticker = matplotlib.ticker.EngFormatter(unit='')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(right=0.77)
    
    ax.set_title("Difference of visits") #, fontweight='bold')
    for i, label in enumerate(countermeasure_names):
        print(label_to_multiline(label))
        ax.plot(date_time, np.asarray(visits_countermeasure[i]), label=label_to_multiline(label))
    ax.yaxis.set_major_formatter(ticker)
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.set_ylabel('People')
    ax.tick_params(axis='x', rotation=30)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute the difference between a standard case and a case with some counter measure applied to them")
    parser.add_argument("--countermeasure_results_dir", type=str, action='append', help="the directory where the counter-measures simulation results are stored")
    parser.add_argument("--countermeasure_name", type=str, action='append', help="The readable name of the countermeasure")

    args = parser.parse_args()
    countermeasure_results_dir = args.countermeasure_results_dir
    countermeasure_name = args.countermeasure_name

    if len(countermeasure_results_dir) == 0 or len(countermeasure_name) != len(countermeasure_results_dir):
        print("Same number of argument required")
        sys.exit(0)
    
    main(countermeasure_results_dir, countermeasure_name)