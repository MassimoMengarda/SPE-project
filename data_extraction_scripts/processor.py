import sys

import pandas as pd

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: PATH/python3 processor.py <input filename> <output filename> <metro area postal codes input filename>")
    
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    filtering_postal_codes_filename = sys.argv[3]

    print("Reading csv file ", filtering_postal_codes_filename)
    zip_codes = pd.read_csv(filtering_postal_codes_filename, converters={'zip_code': str})
    
    print("Reading csv file", input_filename)
    df = pd.read_csv(input_filename, converters={'postal_code': str})

    print("Filtering file")
    df['postal_code'] = df['postal_code'].apply(lambda x: x.zfill(5))
    is_metro_area = df['postal_code'].isin(zip_codes['zip_code'])
    df_metro_area = df[is_metro_area]

    print("Writing csv file", output_filename)
    df_metro_area.to_csv(output_filename, index = False)

if __name__ == "__main__":
    main()
