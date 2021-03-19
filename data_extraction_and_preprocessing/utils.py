import json
import os
from datetime import datetime

def get_dates_from_input_dir(input_dir):
    result = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filename_date = datetime.strptime(filename[:len("2019-01-08")], "%Y-%m-%d")
            new_filename = filename_date.strftime("%Y-%m-%d") + ".csv"
            result.append((new_filename, os.path.join(input_dir, filename)))

    return result

def JSONParser(data):
    return json.loads(data)
