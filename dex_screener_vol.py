import os, requests, json, datetime
from concurrent.futures import ThreadPoolExecutor
from g_trend.send_helper import send_tg, send_error


def dexscreen(key, volume, address):

    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{key}"
        dex = requests.get(url)
        if dex.status_code == 200:
            get_vol(dex, volume, address)
        else:
            send_error(f"dexscreen(): {dex.status_code}")

    except Exception as e:
        send_error(f"dexscreen() requests problem: {e}")
        pass


def get_vol(dex, volume, address):
    if dex == None:
        return
    rson = dex.json()

    if rson["pairs"] == None:
        return

    try:
        for pair in rson['pairs']:
            if pair['dexId'] == "raydium" and pair["quoteToken"]["symbol"] == 'SOL':

                if update and (pair['pairAddress'] in volume):
                    volume[pair['pairAddress']]['volume'].append(
                        {datetime.datetime.now().strftime("%Y-%m-%d"): pair['volume']['h24']})

                else:
                    volume[pair['pairAddress']] = {"name": pair["baseToken"]["name"],
                                                   "symbol": pair["baseToken"]["symbol"],
                                                   "volume": [{datetime.datetime.now().strftime("%Y-%m-%d"):
                                                                pair['volume']['h24']}]}

                address.append(pair['pairAddress'])

    except Exception as e:
        send_error(f"get_vol() for loop: {e}")
        pass

def get_token_address():

    pairadress = []
    addressList = []
    volumedict = {}

    try:
        url = "https://api.raydium.io/v2/main/pairs"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            for i in data:
                pairadress.append(i["ammId"])
                addressList.append(i["baseMint"])
                volumedict[i["baseMint"]] = i["volume24h"]
        else:
            send_error(f"get_token_address(): {response.status_code}")


    except Exception as e:
        send_error(f"get_token_address() requests problem: {e}")
        with open("raydium_backup_pair_list.json", 'r') as f:
            data = json.load(f)
        for i in data:
            pairadress.append(i["ammId"])
            addressList.append(i["baseMint"])
            volumedict[i["baseMint"]] = i["volume24h"]
        pass


    return addressList, pairadress, volumedict


def update():

    volume = {}
    if not os.path.isfile("ray_vol.json"):
        return volume

    with open("ray_vol.json", "r") as f:
        # Load the JSON data
        volume = json.load(f)

    return volume


def fetch_vol(volume, address, Vol, update_, mp_mode):
    count = 0

    try:
        if Vol:
            addressList, pairadress, volumedict = get_token_address()
            if update_:
                volume = update()

            combine_pairList = [",".join(pairadress[i:i + 30]) for i in range(0, len(pairadress), 30)]
            print("total:", len(combine_pairList))



            if mp_mode:
                # Using ThreadPoolExecutor to handle concurrent requests
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(dexscreen, pairs30, volume, address) for pairs30 in combine_pairList]
                    for future in futures:
                        future.result()  # This line will ensure each thread completes before moving on
                        print("num", count)
                        count += 1

            else:
                for pairs30 in combine_pairList:
                    dexscreen(pairs30, volume, address)

            with open("ray_vol.json", 'w') as f:
                json.dump(volume, f)

    except Exception as e:
        send_error(f"fetch_vol(): {e}")