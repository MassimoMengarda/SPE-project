import argparse
import os
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from data_extraction_and_preprocessing.utils import get_dates_from_input_dir

plt.style.use("seaborn-whitegrid")

def main(standard_results_dir, countermeasure_results_dir, countermeasure_name, output_dir):
    dates_paths = get_dates_from_input_dir(standard_results_dir, extension="")
    dates_paths.sort(key=lambda tup: tup[0])

    last_day_susceptible_standard = -1
    last_day_susceptible_countermeasure = -1

    date_time = []
    new_cases_standard = []
    removed_dead_standard = []
    removed_alive_standard = []
    
    new_cases_countermeasure = []
    removed_dead_countermeasure = []
    removed_alive_countermeasure = []
    
    for filename, dir_path in dates_paths:
        for i in range(168):
            date_time.append(datetime.datetime.strptime(filename.strip().strip('/'), '%Y-%m-%d') + datetime.timedelta(hours = i))
            
            epidemiological_simulation_results_standard = np.load(os.path.join(dir_path, f"{i:03}.npy"))
            epidemiological_simulation_results_countermeasure = np.load(os.path.join(countermeasure_results_dir, filename, f"{i:03}.npy"))
            
            average_over_batch_standard = np.sum(np.average(epidemiological_simulation_results_standard, axis=1), axis=2)
            average_over_batch_countermeasure = np.sum(np.average(epidemiological_simulation_results_countermeasure, axis=1), axis=2)
            
            if last_day_susceptible_standard == -1 and last_day_susceptible_countermeasure == -1:
                last_day_susceptible_standard = average_over_batch_standard[4][0] + average_over_batch_standard[3][0]
                last_day_susceptible_countermeasure = average_over_batch_countermeasure[4][0] + average_over_batch_countermeasure[3][0]
                new_cases_standard.append(0)
                new_cases_countermeasure.append(0)
            else:
                new_cases_standard_cumulative = new_cases_standard[-1] + ((average_over_batch_standard[4][0] + average_over_batch_standard[3][0]) - last_day_susceptible_standard)
                new_cases_countermeasure_cumulative = new_cases_countermeasure[-1] + ((average_over_batch_countermeasure[4][0] + average_over_batch_countermeasure[3][0]) - last_day_susceptible_countermeasure)
                new_cases_standard.append(new_cases_standard_cumulative)
                new_cases_countermeasure.append(new_cases_countermeasure_cumulative)
                last_day_susceptible_standard = average_over_batch_standard[4][0] + average_over_batch_standard[3][0]
                last_day_susceptible_countermeasure = average_over_batch_countermeasure[4][0] + average_over_batch_countermeasure[3][0]

            removed_dead_standard.append(average_over_batch_standard[3][0])
            removed_alive_standard.append(average_over_batch_standard[4][0])

            removed_dead_countermeasure.append(average_over_batch_countermeasure[3][0])
            removed_alive_countermeasure.append(average_over_batch_countermeasure[4][0])

            print(f"Done {i}")
        print(f"Done {filename}")
    
    print(removed_dead_standard[-1] - removed_dead_countermeasure[-1])
    print(removed_alive_standard[-1] - removed_alive_countermeasure[-1])

    fig, axs = plt.subplots(1, 2, figsize=(10, 6))
    fig.suptitle(countermeasure_name, fontweight='bold')
    ticker = matplotlib.ticker.EngFormatter(unit='')

    axs[0].set_title("Cumulative cases count")
    axs[0].plot(date_time, np.asarray(new_cases_countermeasure), label='With countermeasure')
    axs[0].plot(date_time, np.asarray(new_cases_standard), label="No countermeasures")
    axs[0].yaxis.set_major_formatter(ticker)
    axs[0].legend(frameon=False)
    axs[0].set_ylabel('People')
    axs[0].tick_params(axis='x', rotation=30)
    
    axs[1].set_title("Cumulative deaths count")
    axs[1].plot(date_time, np.asarray(removed_dead_countermeasure), label='With countermeasure')
    axs[1].plot(date_time, np.asarray(removed_dead_standard), label="No countermeasures")
    axs[1].yaxis.set_major_formatter(ticker)
    axs[1].legend(frameon=False)
    axs[1].set_ylabel('People')
    axs[1].tick_params(axis='x', rotation=30)

    # axs[2].plot(x, np.asarray(removed_alive_countermeasure), label="Healed with")
    # axs[2].plot(x, np.asarray(removed_alive_standard), label="Healed without")

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute the difference between a standard case and a case with some counter measure applied to them")
    parser.add_argument("standard_results_dir", type=str, help="the directory the standard simulation results are stored")
    parser.add_argument("countermeasure_results_dir", type=str, help="the directory where the counter-measures simulation results are stored")
    parser.add_argument("countermeasure_name", type=str, help="The readable name of the countermeasure")
    parser.add_argument("output_dir", type=str, help="the directory where store the result")
    
    args = parser.parse_args()
    standard_results_dir = args.standard_results_dir
    countermeasure_results_dir = args.countermeasure_results_dir
    countermeasure_name = args.countermeasure_name
    output_dir = args.output_dir
    
    main(standard_results_dir, countermeasure_results_dir, countermeasure_name, output_dir)

# python3 -m data_analysis.difference_with_standard ../project-data/results_2019/simulation_result_no_countermeasure/ ../project-data/results_2019/simulation_result_food_only_takeaway/ "Only takeaway from food venues" ../dummy
# python3 -m data_analysis.difference_with_standard ../project-data/results_2019/simulation_result_no_countermeasure/ ../project-data/results_2019/simulation_result_close_cinema/ "Closure cinemas and theaters" ../dummy
# python3 -m data_analysis.difference_with_standard ../project-data/results_2019/simulation_result_no_countermeasure/ ../project-data/results_2019/simulation_result_close_food_activity_after_18/ "Only takeaway from food venues after 18" ../dummy
# python3 -m data_analysis.difference_with_standard ../project-data/results_2019/simulation_result_no_countermeasure/ ../project-data/results_2019/simulation_result_close_religious_org/ "Closure of religious organizations" ../dummy