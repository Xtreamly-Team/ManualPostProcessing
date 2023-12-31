from builtins import Exception
import json
import csv
from pprint import pprint


def load_json_data(file_path):
    jsondata = json.load(open(file_path))
    return jsondata


def save_json_data(data, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)


def load_liquidity_pool_data():
    lp_data = load_json_data('new_data/lp.json')
    swq_data = load_json_data('new_data/swq.json')
    swp_data = load_json_data('new_data/swp.json')
    return lp_data, swq_data, swp_data


def combine(lp_data, swq_data, swp_data):
    for i in range(len(swq_data)):
        print(i)
        hash = swq_data[i]['hash']
        # print(hash)
        blockNumber = swq_data[i]['blockNumber']
        # print(blockNumber)
        associated_swp_data = list(filter(lambda d: d['hash'] == hash, swp_data))
        try:
            if associated_swp_data:
                associated_lp_address = associated_swp_data[0]['poolAddress']
                previous_block = str(int(blockNumber) - 1)
                pprint(f'{blockNumber} vs {previous_block}')
                associated_lp_data = lp_data[previous_block][associated_lp_address]

                swq_data[i]['lp_address'] = associated_lp_address
                swq_data[i]['lp_feeTier'] = associated_lp_data['feeTier']
                swq_data[i]['lp_liquidity'] = associated_lp_data['liquidity']
                swq_data[i]['lp_tvlToken0'] = associated_lp_data['tvlToken0']
                swq_data[i]['lp_tvlToken1'] = associated_lp_data['tvlToken1']
                swq_data[i]['lp_tvlUSD'] = associated_lp_data['tvlUSD']
                swq_data[i]['lp_volumeUSD'] = associated_lp_data['volumeUSD']
                swq_data[i]['lp_volumeUSDChange'] = associated_lp_data['volumeUSDChange']
                swq_data[i]['lp_volumeUSDWeek'] = associated_lp_data['volumeUSDWeek']
                swq_data[i]['token0Price'] = associated_lp_data['token0Price']
                swq_data[i]['token1Price'] = associated_lp_data['token1Price']
            else:
                swq_data[i]['lp_address'] = None
                swq_data[i]['lp_feeTier'] = None
                swq_data[i]['lp_liquidity'] = None
                swq_data[i]['lp_tvlToken0'] = None
                swq_data[i]['lp_tvlToken1'] = None
                swq_data[i]['lp_tvlUSD'] = None
                swq_data[i]['lp_volumeUSD'] = None
                swq_data[i]['lp_volumeUSDChange'] = None
                swq_data[i]['lp_volumeUSDWeek'] = None
                swq_data[i]['token0Price'] = None
                swq_data[i]['token1Price'] = None
        except Exception as e:
            pprint(e)

    return swq_data


if __name__ == '__main__':
    lp_data, swq_data, swp_data = load_liquidity_pool_data()
    combined_data = combine(lp_data, swq_data, swp_data)
    save_json_data(combined_data, 'new_data/combined.json')

    with open('./new_data/output.csv', 'w', newline='') as csvfile:
        fieldnames = combined_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for d in combined_data:
            writer.writerow(d)

