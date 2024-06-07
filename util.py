import os, requests

def change_ip(file) -> list:

    if os.path.isfile(file):
        with open(file, 'r') as file:
            proxies = file.readlines()
        for i in range(len(proxies)):
            proxies[i] = "http://" + proxies[i].strip()
        return proxies

    response = requests.get("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt")
    if response.status_code == 200:
        return response.text.split('\r\n')
    else:
        print(f"requesting Proxy error {response.status_code}")


def increase_vol(vol, ma):
    l = []
    for i in vol:
        token_vol = vol[i]['volume']
        if len(token_vol) > ma:
            if list(token_vol[-1].values())[0] > list(token_vol[-ma].values())[0]:
                l.append(vol[i]['symbol'])
        else:
            l.append(vol[i]['symbol'])
    return l


def cal_ma(df, n):
    try:
        for col in df.columns:
            df[col] = df[col].rolling(window=n).mean()
        df.dropna()
    except Exception as e:
        print(f"ERROR df_ma: {e}")
        pass
    return df
