import sys

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 clean_duplicate_zip_codes.py <input filename> <output filename>")
    
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    print("Reading csv file", input_filename)
    df = pd.read_csv(input_filename, converters={"zip_code": str})

    print("Filtering file")
    new_df = df.drop_duplicates(subset = ["zip_code"])

    print("Writing csv file", output_filename)
    new_df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    main()

