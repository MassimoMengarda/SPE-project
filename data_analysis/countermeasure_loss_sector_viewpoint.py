import argparse
import os
import datetime
from networkx.algorithms.shortest_paths import weighted

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import math

from numerize import numerize
from data_extraction_and_preprocessing.utils import get_dates_from_input_dir, read_csv, read_npy

plt.style.use("seaborn-whitegrid")

def datetime_converter(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d")

def main(io_to_category_filepath, countermeasure_results_dir, countermeasure_name):
    category_df = read_csv(io_to_category_filepath, sep=";")

    fig, axes = plt.subplots(ncols=len(countermeasure_results_dir), sharey=True, figsize=(20, 8))
    fig.suptitle("Economic loss", fontweight='bold')

    for i, countermeasure_dir in enumerate(countermeasure_results_dir):
        countermeasure_data = read_npy(os.path.join(countermeasure_dir, "sector_graph.npy"))
        
        df = pd.DataFrame({'sector_id': countermeasure_data[0], 'initial_value': countermeasure_data[1], 'actual_value': countermeasure_data[2]})
        df = pd.merge(df, category_df, left_on='sector_id', right_on='sector_number')

        df['loss_value'] = df['initial_value'] - df['actual_value']

        df['remain_market_percent'] = (df['actual_value'] / df['initial_value'])
        df['percent_loss'] = 1.0 - df['remain_market_percent']

        df['remain_market_percent'] *= 100
        df['percent_loss'] *= 100

        df.sort_values('percent_loss', inplace=True, ascending=False)

        print(df)

        most_vulnerable_sectors = df.head(5)
        print(most_vulnerable_sectors)

        perc_ticker = matplotlib.ticker.PercentFormatter()
        
        axes[i].bar(most_vulnerable_sectors['name'], most_vulnerable_sectors['remain_market_percent'], color='#d6d6d6', label='Remaining market')
        axes[i].bar(most_vulnerable_sectors['name'], most_vulnerable_sectors['percent_loss'], bottom=most_vulnerable_sectors['remain_market_percent'], color='#f22424', label='Loss market')
        
        for h_pos, (v_pos, value) in enumerate(zip(most_vulnerable_sectors['remain_market_percent'], most_vulnerable_sectors['actual_value'])):
            if v_pos != 0:
                v = str(numerize.numerize(value))
                axes[i].text(get_h_pos(h_pos, v), v_pos / 2 - 1.2, v, color='black', fontweight='bold')

        for h_pos, (v_pos, bottom_pos, value) in enumerate(zip(most_vulnerable_sectors['percent_loss'], most_vulnerable_sectors['remain_market_percent'], most_vulnerable_sectors['loss_value'])):
            if v_pos != 0:
                v = str(numerize.numerize(value))
                axes[i].text(get_h_pos(h_pos, v), v_pos / 2 + bottom_pos - 1.2, v, color='black', fontweight='bold')
        
        axes[i].yaxis.set_major_formatter(perc_ticker)
        axes[i].set_xlabel(countermeasure_name[i], weight='bold')
        axes[i].xaxis.set_label_position('top') 
        axes[i].set_axisbelow(True)

        for tick in axes[i].get_xticklabels():
            tick.set_rotation(45)
            tick.set_ha('right')

    axes[0].set_ylabel('Percentage')
    axes[-1].legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left')
    axes[-1].tick_params(axis=u'both', which=u'both', length=0)
    plt.tight_layout()
    fig.subplots_adjust(wspace=0)
    plt.show()

def get_h_pos(h_pos, value):
    return h_pos - (len(value) * 0.05)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot the actual cases vs the simulated cases")
    parser.add_argument("io_to_category_filepath", type=str, help="the filepath to the file that convert io sector id to sector name")
    parser.add_argument("--countermeasure_results_dir", type=str, action='append', help="the directory where the counter-measures simulation results are stored")
    parser.add_argument("--countermeasure_name", type=str, action='append', help="The readable name of the countermeasure")

    args = parser.parse_args()
    countermeasure_results_dir = args.countermeasure_results_dir
    countermeasure_name = args.countermeasure_name
    io_to_category_filepath = args.io_to_category_filepath
    
    main(io_to_category_filepath, countermeasure_results_dir, countermeasure_name)

# python3 -m data_analysis.countermeasure_loss_sector_viewpoint --countermeasure_results_dir ../project-data/results_2019/simulation_result_food_only_takeaway/ --countermeasure_name "Only takeaway from food venues" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_cinema/ --countermeasure_name "Closure cinemas and theaters" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_food_activity_after_18/  --countermeasure_name "Only takeaway from food venues after 18" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_religious_org/ --countermeasure_name "Closure of religious organizations" /storage/project-data/economics_data/naics_to_io.csv