import os
import pandas as pd
import json

def JSONParser(data):
    j1 = json.loads(data)
    return j1

def main():
    patterns_dir = "/weekly_dir"

    for pattern_file in os.listdir(dir1):
        if pattern_file.endswith(".csv"):
            df = pd.read_csv(os.path.join(patterns_dir, pattern_file), converters={'postal_code':str,'visitor_home_cbgs':JSONParser})
        
        df["raw_visitor_counts"] = df["visitor_home_cbgs"]
        print(df)


if __name__ == "__main__":
    main()