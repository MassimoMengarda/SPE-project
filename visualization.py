import argparse
import os
import sys

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data_extraction_and_preprocessing.utils import read_npy

def main(sim_dir, info_dir, output_dir):
    weeks = os.listdir(sim_dir)
    print(weeks)
    weeks_hour = 24 * 7

    cbgs_population = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
    # cbgs_population = np.reshape(cbgs_population, (1, cbgs_population.shape[0]))

    seir_model = np.zeros((5, 0))
    sample_cbg = 0

    for week in weeks:
        for hour in range(weeks_hour):
            hour_filepath = os.path.join(sim_dir, week, "{:0>3d}.npy".format(hour))
            hour_df = read_npy(hour_filepath)
            seir_model = np.append(seir_model, hour_df[:,0,[sample_cbg]], axis=1)

    # Once per week or total results?
    print(f"Population {cbgs_population[sample_cbg]}")
    print(f"Population {cbgs_population[sample_cbg]}")
    print("Susceptible", seir_model[0][0])
    print("Exposed", seir_model[1][0])
    print("Infectious", seir_model[2][0])
    print("Dead", seir_model[3][167])
    print("Recovered", seir_model[4][0])
    data = {
        "Susceptible": seir_model[0] / cbgs_population[sample_cbg],
        "Exposed": seir_model[1] / cbgs_population[sample_cbg],
        "Infectious": seir_model[2] / cbgs_population[sample_cbg],
        "Dead": seir_model[3] / cbgs_population[sample_cbg],
        "Recovered": seir_model[4] / cbgs_population[sample_cbg]
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
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the index result")
    args = parser.parse_args()
    sim_dir = args.simulation_directory
    info_dir = args.info_directory
    output_dir = args.output_directory
    
    main(sim_dir, info_dir, output_dir)
    