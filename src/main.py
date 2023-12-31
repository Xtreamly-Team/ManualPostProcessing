import csv
import json
import os
from sys import argv
from pprint import pprint
from dataclasses import dataclass, asdict
uniswap_files = [f for f in os.listdir('data/uniswap')]
mempool_files = [f for f in os.listdir('data/mempool')]

mempool_transactions = []
new_mempool_transactions = []
executed_swaps = []
quoted_prices = []
output_data = []

@dataclass
class Output:
    opened_time: int
    closed_time: int
    amount_in: float
    amount_out: float
    executed_price: float
    quote_price: float
    slippage: float
    hash: str
    gas_used: int
    gas_price: int
    sqrt_price: float
    tick: int
    origin: str
    is_buy: bool
    blockNumber: int

def readMempolData():
    global mempool_transactions
    with open('data/mempool_copy.txt', 'r') as file:
        deserialized = json.load(file)
        mempool_transactions = [*deserialized]
        # i = 0
        # for line in file.readlines():
        #     i += 1
        #     # if i > 2:
        #     #     break
        #     if line := line.strip():
        #         if not line.startswith('-'):
        #             mempool_transactions.append(json.loads(line))

    # This is to ensure non transaction data is removed (timestamps, errors, etc)
    real_transactions = [x for x in mempool_transactions if isinstance(x, dict)] 
    mempool_transactions = [*real_transactions]

    for transaction in mempool_transactions:
        transaction['timestamp'] = int(transaction['timestamp'])

def readNewMempoolData():
    global new_mempool_transactions
    for filename in mempool_files:
        try:
            deserialized = json.load(open(f'data/mempool/{filename}', 'r'))
            new_mempool_transactions.append(deserialized)
        except:
            print(f'Failed to decerialize {filename}')
            continue

    new_mempool_transactions = sorted(new_mempool_transactions, key=lambda x: x['Time'])

def readQuotedPrices():
    with open('data/quoted_price.txt', 'r') as file:
        i = 0
        for line in file.readlines():
            i += 1
            # if i > 5:
            #     break
            if line := line.strip():
                quoted_prices.append(json.loads(line))

    for quote in quoted_prices:
        quote['timestamp'] = int(quote['timestamp'] / 1000)

def readExecutedSwapsData():
    i = 0
    print(f'All swaps {len(uniswap_files)}')
    for filename in uniswap_files:
        i += 1
        # if i > 5:
        #     break
        with open(f'data/uniswap/{filename}', 'r') as file:
            try: 
                decerialized = json.loads(file.read())
                transaction = decerialized['Swap']['transaction']
                timestamp = int(transaction['timestamp'])
                # Make sure the swap is newer than the first mempool transaction
                if timestamp > (new_mempool_transactions[0]['Time'] // 1000):
                    # Make sure the transaction is correct formated and has a block number
                    if transaction['blockNumber']:
                        executed_swaps.append(decerialized)
            except:
                # print(filename)
                continue
    print(f'Swaps starting newer than mempool files: {len(executed_swaps)}')


def get_nearest_quote(timestamp: int):
    nearest_quote = quoted_prices[0]
    for i, quote in enumerate(quoted_prices):
        if quote['timestamp'] <= timestamp:
            if quote['timestamp'] > nearest_quote['timestamp']:
                nearest_quote = quote
    return nearest_quote

if __name__ == '__main__':
    readQuotedPrices()
    print(f"Total quoted prices {len(quoted_prices)}")
    readNewMempoolData()
    print(f"Total mempool transactions {len(new_mempool_transactions)}")
    readExecutedSwapsData()
    if len(argv) > 1 and argv[1] == 'assumption':
        for swap_item in executed_swaps:
            nearest_quote = quoted_prices[0]
            swap = swap_item['Swap']
            transaction = swap['transaction']
            transaction_hash = transaction['id']
            nearest_quote = get_nearest_quote(int(transaction['timestamp']) - 6)


            output = Output(
                opened_time=nearest_quote['timestamp'],
                closed_time=int(transaction['timestamp']),
                amount_in=abs(float(swap['amount0'])),
                amount_out=abs(float(swap['amount1'])),
                executed_price=swap_item['ExecutedPrice'],
                quote_price=nearest_quote['price'],
                slippage=nearest_quote['price'] - swap_item['ExecutedPrice'],
                hash=transaction_hash,
                gas_used=int(transaction['gasUsed']),
                gas_price=int(transaction['gasPrice']),
                sqrt_price=float(swap['sqrtPriceX96']),
                tick=int(swap['tick']),
                origin=swap['origin'],
                is_buy=swap_item['IsBuy'],
                blockNumber=transaction['blockNumber']
            )

            output_data.append(output)

    else:
        # readMempolData()

        new_mempool_transaction_hashes = list(map(lambda x: x['Tx'], new_mempool_transactions))

        j = 0

        for swap_item in executed_swaps:
            j += 1
            print(j)
            swap = swap_item['Swap']
            transaction = swap['transaction']
            transaction_hash = transaction['id']
            if not transaction_hash in new_mempool_transaction_hashes:
                continue
            matched_memepool_transaction = list(filter(lambda x: x['Tx'] == transaction_hash, new_mempool_transactions))[0]
            swap_starting_time = matched_memepool_transaction['Time'] // 1000

            nearest_quote = get_nearest_quote(swap_starting_time)

            output = Output(
                opened_time=swap_starting_time,
                closed_time=int(transaction['timestamp']),
                amount_in=abs(float(swap['amount0'])),
                amount_out=abs(float(swap['amount1'])),
                executed_price=swap_item['ExecutedPrice'],
                quote_price=nearest_quote['price'],
                slippage=nearest_quote['price'] - swap_item['ExecutedPrice'],
                hash=transaction_hash,
                gas_used=int(transaction['gasUsed']),
                gas_price=int(transaction['gasPrice']),
                sqrt_price=float(swap['sqrtPriceX96']),
                tick=int(swap['tick']),
                origin=swap['origin'],
                is_buy=swap_item['IsBuy'],
                blockNumber=transaction['blockNumber']
            )

            output_data.append(output)

    print(f"Total swaps matched with mempool {len(output_data)}")
    with open('./data/output.csv', 'w', newline='') as csvfile:
        output_dicts = [asdict(output) for output in output_data]
        fieldnames = output_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for d in output_dicts:
            writer.writerow(d)

    json.dump([asdict(output) for output in output_data], open('data/output.json', 'w'), indent=4)



            


