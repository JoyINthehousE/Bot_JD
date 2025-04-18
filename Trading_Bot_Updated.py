import hmac
import hashlib
import base64
import json
import time
import requests
import pandas as pd
import pandas_ta as ta
import datetime as dt
import numpy as np
import streamlit as st


# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = "18672fb65b1378d14c06ce568317a2ef210e5dab92326d63"
secret = "79a62e7fe54d655e87198c443a006816431cd306fad2c088252f1dd1bdf52925"

# python3
secret_bytes = bytes(secret, encoding='utf-8')


#Market Candles Data Generator
url_ticker = "https://api.coindcx.com/exchange/ticker"
response_markets = requests.get(url_ticker)
data = response_markets.json()
markets_df = pd.DataFrame(data)

# Ensure last_price is converted to numeric, errors='coerce' will convert invalid parsing to NaN
inr_candles = []

# Now perform the comparison safely
# Your code logic here
for i in markets_df['market']:
    Uprice = float(markets_df.loc[markets_df['market'] == i, 'last_price'].values[0])
    if i[-3:] == 'INR' and (Uprice <= 100 and Uprice > 0.01):
        inr_candles.append(i)

df_data = pd.DataFrame(columns = inr_candles)

# Generating a timestamp.
timeStamp = int(round(time.time() * 1000))

#Order creation
def order(side: str, symbol: str, t_q: float, price: float):
    body = {
    "side": side,    #Toggle between 'buy' or 'sell'.
    "order_type": "limit_order", #Toggle between a 'market_order' or 'limit_order'.
    "market": symbol, #Replace 'SNTBTC' with your desired market pair.
    "price_per_unit": price, #This parameter is only required for a 'limit_order'
    "total_quantity": t_q, #Replace this with the quantity you want
    "timestamp": timeStamp,
    }
    
    json_body = json.dumps(body, separators = (',', ':'))
    
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    
    url_order = "https://api.coindcx.com/exchange/v1/orders/create"
    
    headers = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': key,
    'X-AUTH-SIGNATURE': signature
    }
    
    response_order = requests.post(url_order, data = json_body, headers = headers)
    print(symbol, side, pd.DataFrame(response_order))
    
while True:
    secret_bytes = bytes(secret, encoding='utf-8')

    # Generating a timestamp
    timeStamp = int(round(time.time() * 1000))

    body = {
        "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators = (',', ':'))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url_balances = "https://api.coindcx.com/exchange/v1/users/balances"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response_account = requests.post(url_balances, data = json_body, headers = headers)
    data_account = response_account.json();
    df_account = pd.DataFrame(data_account)
    print(df_account)
    url_ticker = "https://api.coindcx.com/exchange/ticker"
    response_markets = requests.get(url_ticker)
    data = response_markets.json()
    markets_df = pd.DataFrame(data)

    for name in df_account['currency']:
        bitch = name + '_INR'
        url_candles  = f"https://public.coindcx.com/market_data/candles?pair=I-{bitch}&interval=30m"
        response_price = requests.get(url_candles)
        data_price = response_price.json()
        df_price = pd.DataFrame(data_price)
        t3_fast = ta.t3(df_price['close'], timeperiod = 8, vfactor = 0.7)
        t3_slow = ta.t3(df_price['close'], timeperiod = 13, vfactor = 0.6)
        t3_slow_cleared = t3_slow.dropna()
        t3_fast_cleared = t3_fast.dropna()
        if not t3_slow_cleared.empty and not t3_fast_cleared.empty:
            if t3_slow_cleared.iloc[-1] > t3_fast_cleared.iloc[-1]:
                st.write(f"sell {name}")
        
    for name in inr_candles:
        bitch = name[:-3] + '_' + name[-3:]
        url_candles  = f"https://public.coindcx.com/market_data/candles?pair=I-{bitch}&interval=30m"
        response_price = requests.get(url_candles)
        df_price = pd.DataFrame(data_price)
        t3_fast = ta.t3(df_price['close'], timeperiod = 8, vfactor = 0.7)
        t3_slow = ta.t3(df_price['close'], timeperiod = 13, vfactor = 0.6)
        t3_slow_cleared = t3_slow.dropna()
        t3_fast_cleared = t3_fast.dropna()
        if not t3_slow_cleared.empty and not t3_fast_cleared.empty:
            if t3_slow_cleared.iloc[-1] > t3_fast_cleared.iloc[-1]:
                st.write(f"buy {name}")
