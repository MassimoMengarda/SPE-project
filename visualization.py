import argparse
import os
import sys

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data_extraction_and_preprocessing.utils import read_csv, read_npy

def main(sim_dir, output_dir):
    weeks = os.listdir(sim_dir)
    weeks_hour = 24 * 7

    seir_model = np.zeros((5, 0))

    for week in weeks:
        for hour in range(weeks_hour):
            hour_filepath = os.path.join(sim_dir, week, "{:0>3d}.npy".format(hour))
            hour_df = read_npy(hour_filepath)
            seir_model = np.append(seir_model, hour_df[:,0,[0]], axis=1)

    # Once per week or total results?
    data = {
        "Susceptible": seir_model[0],
        "Exposed": seir_model[1],
        "Infectious": seir_model[2],
        "Dead": seir_model[3],
        "Recovered": seir_model[4]
    }
    df = pd.DataFrame(data=data)
    sns.lineplot(data=df)
    plt.show()
    # dots = sns.load_dataset("dots")
    # sns.relplot(
    #     data=df, kind="line",
    #     x="time", y="cbg", col="align",
    #     hue="choice", size="coherence", style="choice",
    #     facet_kws=dict(sharex=False),
    # )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("simulation_directory", type=str, help="the directory where the simulation results are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the index result")
    args = parser.parse_args()
    sim_dir = args.simulation_directory
    output_dir = args.output_directory
    
    main(sim_dir, output_dir)
    