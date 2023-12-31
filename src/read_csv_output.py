# Read csv to dict
import csv
import os
import sys
import json

def read_csv_output(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        output = list(reader)[0]
    return output

def read_csv_output_dict_list(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        output = list(reader)
    return output

def read_json_output_dict(json_file):
    with open(json_file, 'r') as f:
        output = json.load(f)
    return output

def read_previous_output(csv_file):
    if os.path.exists(csv_file):
        return read_csv_output_dict_list(csv_file)
    else:
        return []

def write_dict_list_to_json(dict_list, json_file):
    with open(json_file, 'w') as f:
        json.dump(dict_list, f)

def augment_output(previous_dict_list ,new_dict):
    result = []
    for previous_dict_item in previous_dict_list:
        block_number = previous_dict_item['blockNumber']
        pools_data = {'pools': new_dict[block_number]}
        previous_dict_item = {** previous_dict_item, ** (pools_data)}
        result.append(previous_dict_item)
    return result
    

def main():
    json_file = sys.argv[1]
    csv_file = sys.argv[2]
    pools_data_dict = read_json_output_dict(json_file)
    transaction_data_list = read_csv_output_dict_list(csv_file)
    res = augment_output(transaction_data_list, pools_data_dict)
    write_dict_list_to_json(res, './transactions_and_pools.json')

if __name__ == '__main__':
    main()
