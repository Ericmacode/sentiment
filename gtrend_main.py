import time
import pandas as pd
import numpy as np
import datetime, json
from pytrends.request import TrendReq
from tqdm import tqdm
from g_trend2.send_helper import send_tg, send_error
from g_trend2.util import change_ip, increase_vol, cal_ma
from g_trend2.dex_screener_vol import fetch_vol

def get_google_trend(token, ma, proxies, num, k):
    df = pd.DataFrame()
    try:
        print([proxies[num + k]])
        # Increase retries and timeout settings
        pytrend = TrendReq(proxies=[proxies[num + k], ], retries=3, backoff_factor=0.1, timeout=10)
        pytrend.build_payload(kw_list=token, timeframe='today 1-m')
        df = pytrend.interest_over_time().tail(ma * 2)
        if not df.empty:
            df = df[token]

            df.drop(df.tail(1).index,inplace=True)

            print(df)
            return df  # Return if successful
        else:
            print(f"df is empty: {token}")
            # If df is empty, no need to try other proxies

    except Exception as e:
        k += 1
        if k == 5 and token != ['solana']:
            print(f"df is empty: {token}, {e}")

            return df
        send_error(f"ERROR Retry: {token}, {e}")
        get_google_trend(token, ma, proxies, num, k)

        time.sleep(5)

    return df


def cal_sentiment_send(df, threshold):
    # try:

    print('the df', df)
    if df.iloc[-1, 0] == np.nan:
        date = pd.to_datetime(
            (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
    else:
        date = pd.to_datetime(
            (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))

    df = df.tail(1).transpose()
    main_token = df.iloc[0, 0]

    # print(df[date] / main)
    print(type(list(df.columns)[0]))
    print(df)

    df['logic'] = np.where(df[date] / (max(1, main_token)) > threshold, 1, 0)
    df['larger'] = np.where(df['logic'] == 1, df.index, '')
    df['smaller'] = np.where(df['logic'] == 0, df.index, '')

    larger_str = ''
    larger = df['larger'].unique()
    larger = list(larger)
    if '' in larger: larger.remove('')
    for token in larger:
        print(token)
        senti = df.loc[token, date]
        larger_str += f"{token} : {senti}\n"

    smaller_str = ''
    smaller = df['smaller'].unique()
    smaller = list(smaller)
    print('smaller list', smaller)
    if '' in smaller: smaller.remove('')
    for token in smaller:
        print(token)
        senti = df.loc[token, date]
        smaller_str += f"{token} : {senti}\n"

    if len(larger) > 0:
        msg = f"SOL : {main_token}\n"
        msg += "tokens with higher sentiment level than SOL\n"
        msg += larger_str
        return msg

    elif len(smaller) > 0:

        msg = "Tokens with lower sentiment level than SOL\n"
        msg += smaller_str
        return msg

    else:
        return ''


# except Exception as e:
#     send_error(f"ERROR cal_sentiment_send: {e}")
#     return ''



def gtrend_main(proxies):
    # try:
    with open("ray_vol.json", "r") as f:
        volume = json.load(f)

    Tokenlist = increase_vol(volume, ma)
    # Tokenlist = ['MOTHER']
    print(Tokenlist)

    # send_tg(f"length: {len(Tokenlist)} \nTesting: {Tokenlist}")

    for k in range(len(Tokenlist)):
        Tokenlist[k] = Tokenlist[k] + " token"

    df = get_google_trend(["solana"], ma, proxies, 0, 0)

    for sec in tqdm(range(sleep)):
        time.sleep(1)

    for i in range(len(Tokenlist)):
        # proxy_list = proxies[i:i+3] if i < len(proxies)-1 else proxies[i%len(proxies):i%len(proxies)+3]
        num = i % (len(proxies) - 7) + 3

        print(Tokenlist[i])
        df2 = get_google_trend([Tokenlist[i]], ma=ma, proxies=proxies, num=num, k=0)

        for sec in tqdm(range(sleep)):
            time.sleep(1)

        if not df2.empty:
            print(df, df2)
            df3 = pd.concat([df, df2], axis=1)
            print("concat")
            print(df3)

            # if (i+1) % 1 == 0:
            df3 = cal_ma(df3, n=ma)
            msg = cal_sentiment_send(df3, threshold=threshold)
            send_tg(msg)

            print(f"{i + 1} is done")

    df = cal_ma(df, n=ma)
    msg = cal_sentiment_send(df, threshold=threshold)
    send_tg(msg)


# except Exception as e:
#     send_error(f"gtrend_main(): {e}")

# except Exception as e:
#     send_error(f"gtrend_main(): {e}")


#######################################################################
if "__main__" == __name__:
    # send_tg("SOL Sentiment Score: 72 \n"
    #         "Tokens with Higher Sentiment Level than SOL: \n"
    #         "BONK score: 85")
    # ######## set parameters #############
    # google
    ma = 3
    threshold = 1
    sleep = 25

    volume_data = {}
    address = []

    # volume
    Vol = True
    update_ = True
    mp_mode = True
    ip_file = "proxy_list.txt"

    send_tg(f'V1.1\n'
            f'MA: {ma}\n'
            f'THRESHOLD: {threshold * 100}%\n'
            f'SLEEP: {sleep}\n'
            f'MULTI THREAD: {mp_mode}')

    #####################################

    while (True):
        # now = datetime.datetime.now()
        # if (now.hour == 0 and now.minute == 0):
        proxies = change_ip(ip_file)
        # fetch_vol(volume_data, address, Vol, update_, mp_mode)
        gtrend_main(proxies=proxies)
        # break