import sys
import os

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 population_filter.py <input directory> <zip cbg join filename> <output directory>")
    
    input_directory = sys.argv[1]
    zip_cbg_filename = sys.argv[2]
    output_directory = sys.argv[3]

    if not os.path.isdir(input_directory):
        sys.exit(f"Error: {input_directory} is not a valid directory")

    if not os.path.isdir(output_directory):
        sys.exit(f"Error: {output_directory} is not a valid directory")
    
    data_directory = os.path.join(input_directory, "data")
    paths = [(filename, os.path.join(data_directory, filename)) for filename in os.listdir(data_directory) if filename.endswith(".csv") and filename != "cbg_patterns.csv"]

    if len(paths) == 0:
        sys.exit(f"Error: no csv file were find in directory {data_directory}")

    fields_filepath = os.path.join(input_directory, "metadata", "cbg_field_descriptions.csv")
    print("Reading csv file", fields_filepath)
    fields = pd.read_csv(fields_filepath)
    fields_mapping = pd.Series(fields["field_full_name"].values,index=fields["table_id"]).to_dict()

    print("Reading csv file", zip_cbg_filename)
    zip_code_cbg_map = pd.read_csv(zip_cbg_filename, converters={"zip_code": str, "cbg": str})

    cbg_patterns_file = os.path.join(input_directory, "data", "cbg_patterns.csv")
    print("Reading csv file", cbg_patterns_file)
    df = pd.read_csv(cbg_patterns_file, converters={"census_block_group":str})
    is_metro_area = df["census_block_group"].isin(zip_code_cbg_map["cbg"])
    df = df[is_metro_area]
    cbg_patterns_output_filename = os.path.join(output_directory, "cbg_patterns.csv")
    df.to_csv(cbg_patterns_output_filename, index=False)
    
    for filename, path in paths:
        print("Reading csv file", path)
        df = pd.read_csv(path, converters={"census_block_group": str})
        is_metro_area = df["census_block_group"].isin(zip_code_cbg_map["cbg"])
        df = df[is_metro_area]

        df.rename(columns=fields_mapping, inplace=True)

        output_filename = os.path.join(output_directory, filename)
        print("Writing csv file", output_filename)
        df.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
