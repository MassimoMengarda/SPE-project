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
M = 1000000

def label_to_multiline(label : str) -> str:
    return ' '.join([x + ("\n" if (i + 1) % 3 == 0 else "") for i, x in enumerate(label.split(" "))])

def datetime_converter(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d")

def main(io_to_category_filepath, countermeasure_results_dirs, countermeasure_names):
    category_df = read_csv(io_to_category_filepath, sep=";")

    most_vulnerable_sectors_for_countermeasure = []
    df_countermeasures = []

    total_loss_countermeasures = []
    other_loss_countermeasures = []
    other_loss_countermeasures_percent = []

    money_graph = [[] for i in range(len(countermeasure_results_dirs))]
    perc_graph = [[] for i in range(len(countermeasure_results_dirs))]

    for i, countermeasure_dir in enumerate(countermeasure_results_dirs):
        countermeasure_data = read_npy(os.path.join(countermeasure_dir, "sector_graph.npy"))
        
        df = pd.DataFrame({'sector_id': countermeasure_data[0], 'initial_value': countermeasure_data[1] / M, 'actual_value': countermeasure_data[2] / M})
        df = pd.merge(df, category_df, left_on='sector_id', right_on='sector_number')

        df['loss_value'] = df['initial_value'] - df['actual_value']

        df['remain_market_percent'] = (df['actual_value'] / df['initial_value'])
        df['percent_loss'] = 1.0 - df['remain_market_percent']

        df['remain_market_percent'] *= 100
        df['percent_loss'] *= 100

        df.sort_values('loss_value', inplace=True, ascending=False)

        most_vulnerable_sectors = df.head(5)

        total_loss_countermeasure = df['loss_value'].sum()
        total_loss_countermeasures.append(total_loss_countermeasure)

        most_vulnerable_sectors_for_countermeasure.append(most_vulnerable_sectors)
        df_countermeasures.append(df)
    
    print(total_loss_countermeasures)
    print(countermeasure_names)
    
    mvsc_sec_id_list = most_vulnerable_sectors_for_countermeasure[0]['sector_id'].to_numpy()
    i = 1
    while i < len(most_vulnerable_sectors_for_countermeasure):
        mvsc_sec_id_list = np.append(mvsc_sec_id_list, most_vulnerable_sectors_for_countermeasure[i]['sector_id'].to_numpy())
        i += 1
    
    sectors_to_plot = pd.Series(np.unique(mvsc_sec_id_list))

    cmap = matplotlib.cm.get_cmap('Spectral')

    sector_colors = cmap(np.linspace(0.0, 1.0, len(sectors_to_plot) + 1))

    for i, df in enumerate(df_countermeasures):
        other_loss_countermeasure = total_loss_countermeasures[i] - df[df['sector_id'].isin(sectors_to_plot)]['loss_value'].sum()

        other_loss_countermeasures.append(other_loss_countermeasure)
        other_loss_countermeasures_percent.append((other_loss_countermeasure / total_loss_countermeasures[i]) * 100)

    

    # for i in range():

    fig, axes = plt.subplots(ncols=2, figsize=(20, 8))
    fig.subplots_adjust(right=0.85, bottom=0.25)
    fig.suptitle("Economic loss", fontweight='bold')

    axes[0].bar(countermeasure_names, other_loss_countermeasures, color = sector_colors[0])
    axes[1].bar(countermeasure_names, other_loss_countermeasures_percent, color = sector_colors[0])

    bottom_money = np.asarray(other_loss_countermeasures)
    bottom_percent = np.asarray(other_loss_countermeasures_percent)
    
    for sector_plot_idx, sector in enumerate(sectors_to_plot):
        loss_value_sector = []
        for df in df_countermeasures:
            loss_value_sector.append(df[df['sector_id'] == sector].iloc[0]['loss_value'])
        for i in range(len(money_graph)):
            money_graph[i].append((loss_value_sector[i], sector_colors[sector_plot_idx + 1]))

        loss_percentage_sector = np.asarray(loss_value_sector) / np.asarray(total_loss_countermeasures) * 100
        for i in range(len(perc_graph)):
            perc_graph[i].append((loss_percentage_sector[i], sector_colors[sector_plot_idx + 1]))
    
    sorted_money_graph = []
    for i in range(len(money_graph)):
        sorted_money_graph.append(sorted(money_graph[i], key=lambda x : x[0]))
    
    sorted_perc_graph = []
    for i in range(len(perc_graph)):
        sorted_perc_graph.append(sorted(perc_graph[i], key=lambda x : x[0]))
    
    for i in range(len(sorted_money_graph[0])):
        color_value = []
        values = []
        for j in range(len(sorted_money_graph)):
            values.append(sorted_money_graph[j][i][0])
            color_value.append(sorted_money_graph[j][i][1])
        values_np = np.asarray(values)
        axes[0].bar(countermeasure_names, values_np, bottom = bottom_money, color = color_value)
        bottom_money += values_np
    
    for i in range(len(sorted_perc_graph[0])):
        color_value = []
        values = []
        for j in range(len(sorted_perc_graph)):
            values.append(sorted_perc_graph[j][i][0])
            color_value.append(sorted_perc_graph[j][i][1])
        values_np = np.asarray(values)
        axes[1].bar(countermeasure_names, values_np, bottom = bottom_percent, color = color_value)
        bottom_percent += values_np
    
    

    num_ticker = matplotlib.ticker.EngFormatter(unit='')
    axes[0].yaxis.set_major_formatter(num_ticker)
    axes[0].set_ylabel('Milions of dollars')
    
    perc_ticker = matplotlib.ticker.PercentFormatter()
    axes[1].yaxis.set_major_formatter(perc_ticker)
    axes[1].set_ylabel('Percentage')

    for ax in axes:
        for tick in ax.get_xticklabels():
            tick.set_rotation(20)
            tick.set_ha('right')
    
    legend_handles = []

    for i in range(len(sectors_to_plot)):
        sector_name = category_df[category_df['sector_number'] == sectors_to_plot[i]].iloc[0]['name']
        path = matplotlib.patches.Patch(color=sector_colors[i + 1], label=label_to_multiline(sector_name))
        legend_handles.append(path)
    
    other_path = matplotlib.patches.Patch(color=sector_colors[0], label=label_to_multiline('Other'))
    legend_handles.append(other_path)

    axes[1].legend(handles=legend_handles, frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot the actual cases vs the simulated cases")
    parser.add_argument("io_to_category_filepath", type=str, help="the filepath to the file that convert io sector id to sector name")
    parser.add_argument("--countermeasure_results_dir", type=str, action='append', help="the directory where the counter-measures simulation results are stored")
    parser.add_argument("--countermeasure_name", type=str, action='append', help="The readable name of the countermeasure")

    args = parser.parse_args()
    countermeasure_results_dirs = args.countermeasure_results_dir
    countermeasure_names = args.countermeasure_name
    io_to_category_filepath = args.io_to_category_filepath
    
    main(io_to_category_filepath, countermeasure_results_dirs, countermeasure_names)

# python3 -m data_analysis.countermeasure_loss_millions --countermeasure_results_dir ../project-data/results_2019/simulation_result_food_only_takeaway/ --countermeasure_name "Only takeaway from food venues" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_cinema/ --countermeasure_name "Closure cinemas and theaters" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_food_activity_after_18/  --countermeasure_name "Only takeaway from food venues after 18" --countermeasure_results_dir ../project-data/results_2019/simulation_result_close_religious_org/ --countermeasure_name "Closure of religious organizations" /storage/project-data/economics_data/naics_to_io.csv