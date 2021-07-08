import argparse
import pandas as pd

def main(grid_search_result_filepath):
    grid_search_df = pd.read_csv(grid_search_result_filepath, sep=';')
    best_element = grid_search_df['rmse'].argmin()
    
    print("Best parameters:")
    print(grid_search_df.loc[best_element])

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("grid_search_result_filepath", type=str, help="the filepath where the grid search results are stored")
    args = parser.parse_args()
    grid_search_result_filepath = args.grid_search_result_filepath
    
    main(grid_search_result_filepath)
