import pandas as pd
import json
from argparse import ArgumentParser
import gc
import os
import glob

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-d', required=True, help='path to all metrics files')
    return parser.parse_args()

df = pd.DataFrame(columns = [1,2,3,4,8,9,10,11,12,5,6,7])
row_names = []

def main (metrix_directory):
    print(metrix_directory)
    
    files_list = glob.glob(os.path.join(metrix_directory,"*"))

    print(metrix_directory)
    print(files_list)
    for file in files_list:
        with open(os.path.join(file,'metrics.json'), 'r') as f:
            json_data = json.load(f)
        data_list = []
        columns_names_list = []
        for key in json_data:
            dicts =json_data.get(key)
            for dict_keys in dicts:
            	col_names = f"{key}_{dict_keys}"
            	columns_names_list.append(col_names)
            	data = dicts[dict_keys]
            	data_list.append(data)
        df.columns=columns_names_list
        df.loc[len(df.index)] = data_list
    df.index = files_list
    df.to_csv(metrix_directory+"/metrics_accumulated.csv")
if __name__ == '__main__':
    args = parse_args()
    main(args.d)

