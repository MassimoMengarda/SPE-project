import os
import pandas as pd
import json

def JSONParser(data):
    j1 = json.loads(data)
    return j1

def main():
    dir1 = "/weekly_dir"

    for pattern_file in os.listdir(dir1):
        df = pd.read_csv("/weekly_pattern_link.csv", converters={'postal_code':str,'visitor_home_cbgs':JSONParser})

        df["raw_visitor_counts"]  df["visitor_home_cbgs"]
        print(df)


if __name__ == "__main__":
    main()