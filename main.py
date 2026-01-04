from SmartApi import SmartConnect
from smartWebSocketV2 import SmartWebSocketV2
from config import apikey, username, pwd, token
import pyotp
import json
import http.client
import pandas as pd
from datetime import datetime, timedelta
from logzero import logger


conn = http.client.HTTPSConnection("apiconnect.angelone.in")

symboltoken = int(input("Enter Symbol Token: "))

todate = datetime.now()
fromdate = todate - timedelta(days=30)


obj = SmartConnect(api_key=apikey)
data = obj.generateSession(username, pwd, pyotp.TOTP(token).now())
AUTH_TOKEN = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
FEED_TOKEN = obj.getfeedToken()
res = obj.getProfile(refreshToken)

# WebSocket setup
correlation_id = "abc123"
action = 1
mode = 1

token_list = [{"exchangeType": 1, "tokens":' [f"{symboltoken}"]'}]

sws = SmartWebSocketV2(AUTH_TOKEN, apikey, username, FEED_TOKEN)

def on_data(wsapp, message):
    try:
        last_traded_price = message.get('last_traded_price', 'N/A')
        logger.info(f"LTP: {last_traded_price}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_open(wsapp):
    logger.info("WebSocket Opened")
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    logger.error(f"WebSocket Error: {error}")

def on_close(wsapp):
    logger.info("WebSocket Closed")


api_key = 'gVTQXkoG'
username = 'G52021525'
pwd = '3494'
smartApi = SmartConnect(api_key)

try:
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token.")
    raise e

data = smartApi.generateSession(username, pwd, totp)

if data['status']:
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res = res['data']['exchanges']
else:
    print("Error in generating session")

# HTTP headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-UserType': 'USER',
    'X-SourceID': 'WEB',
    'Authorization': f'{authToken}',
    'X-ClientLocalIP': '192.168.1.13',
    'X-ClientPublicIP': '223.185.133.146',
    'X-MACAddress': 'B6-8C-9D-52-B7-AB',
    'X-PrivateKey': f'{apikey}',
}

# LTP
payload = json.dumps({
    "mode": "OHLC","exchangeTokens": 
    {"NSE": [f"{symboltoken}"]}
}).encode("utf-8")

conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)
res = conn.getresponse()
data = res.read()

try:
    response_dict = json.loads(data.decode("utf-8"))
    if response_dict["status"]:
        fetched_data = response_dict["data"]["fetched"][0]
        print(f"{fetched_data['tradingSymbol']}")
        print(f"LTP: {fetched_data['ltp']}")
    else:
        print("API returned an error.")
except json.JSONDecodeError:
    print("Failed to decode JSON.")

# OHLC
payloadH = json.dumps({
    "exchange": "NSE",
    "symboltoken": f"{symboltoken}",
    "interval": "ONE_DAY",
    "fromdate": fromdate.strftime("%Y-%m-%d %H:%M"),
    "todate": todate.strftime("%Y-%m-%d %H:%M")
}).encode("utf-8")

conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payloadH, headers)
res = conn.getresponse()
data = res.read()

response = json.loads(data.decode("utf-8"))
if response.get("status") and "data" in response:
    candle_data = response["data"]
    df = pd.DataFrame(candle_data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
    df = df.iloc[::-1].reset_index(drop=True)
    print(df)
else:
    print("Error fetching historical data.")

# WebSocket connection
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close
sws.connect()
