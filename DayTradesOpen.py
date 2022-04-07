import csv, json, requests, configparser, datetime, time, atexit
from requests.structures import CaseInsensitiveDict

config = configparser.ConfigParser()
config.read('TOS.ini')

AccessURL = "https://api.tdameritrade.com/v1/oauth2/token"
r = requests.post(url=AccessURL, data= {
    'grant_type': 'refresh_token',
    'refresh_token': config['LoginInfo']['refresh_token'],
    'client_id': config['LoginInfo']['ApiKey']
    })
print(r.status_code, r.json())
AccessResp = r.json()
access_tokenStr = str('Bearer ' + AccessResp['access_token'])
print(access_tokenStr)
BalrURL = ("https://api.tdameritrade.com/v1/accounts/" + config['LoginInfo']['AcctNo'])
Balr = requests.get(url=BalrURL, headers={'Authorization': access_tokenStr})
BalResp = Balr.json()
print(BalResp['securitiesAccount']['currentBalances'])


cashAvail = float(BalResp['securitiesAccount']['currentBalances']['liquidationValue'])
PerBuyCash = (cashAvail-26000)/100
#PerBuyCash = 500
print(PerBuyCash)
StartTime = datetime.datetime.now()


print("time at start for trading:", datetime.datetime.now())
TradedSum = float()
with open('DailyData.csv') as file:
    reader = csv.reader(file)
    factorList = list(reader)

for row in factorList[1:]:
    try:
        response = requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + row[0] +
                                "&apikey=" + config['LoginInfo']['AlphaAPIKey'])
        data = response.json()
        with open('stock_data.json', 'w') as outfile:
            json.dump(data, outfile)
        with open('stock_data.json', 'r') as f:
            PrePreppedData = json.load(f)
            Price = float(PrePreppedData['Global Quote']['05. price'])
            ChgPct = Price/float(PrePreppedData['Global Quote']['08. previous close'])
            Low = float(PrePreppedData['Global Quote']['04. low'])
            AfterLowSwing = Price/Low
            #print(row[0], Price, ChgPct, AfterLowSwing)
            PriceString = str(Price)

            if float(PriceString) > 2:
                SharesToBuy = str(int(PerBuyCash / Price))
                TradedSum = TradedSum + float(SharesToBuy) * Price
                BuyPrice = round((float(row[2]) * 0.993018812), 2)
                SellPrice = round((float(row[2]) * 1.011), 2)
                if TradedSum >= float(cashAvail):
                    print("Last Symbol for the day, not yet bought:", row[0])
                    break
                else:
                    OrderData = {
                        "orderType": "LIMIT",
                        "session": "NORMAL",
                        "price": BuyPrice,
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {
                                "instruction": "Buy",
                                "quantity": SharesToBuy,
                                "instrument": {
                                    "symbol": row[0],
                                    "assetType": "EQUITY"
                                }
                            }
                        ],
                        "childOrderStrategies": [
                            {
                              "orderType": "LIMIT",
                              "session": "NORMAL",
                              "price": SellPrice,
                              "duration": "DAY",
                              "orderStrategyType": "SINGLE",
                              "orderLegCollection": [
                                {
                                  "instruction": "SELL",
                                  "quantity": SharesToBuy,
                                  "instrument": {
                                    "symbol": row[0],
                                    "assetType": "EQUITY"
                                  }
                                }
                              ]
                            }
                          ]
                    }

                    headers = CaseInsensitiveDict()
                    headers["Content-Type"] = "application/json"
                    headers["Authorization"] = access_tokenStr
                    time.sleep(0.7)

                    OrderURL = ("https://api.tdameritrade.com/v1/accounts/" + config['LoginInfo']['AcctNo'] + "/orders")
                    PlaceOrder = requests.post(url=OrderURL, headers=headers, json=OrderData)
                    print(PlaceOrder.status_code, PlaceOrder.json())
                    """print("Symbol:", row[0], "Change Percent", ChgPct,
                              "Shares to Buy", SharesToBuy, "Median Upswing", row[2])"""
                    if PlaceOrder.status_code == 500:
                        with open('Error.csv', 'a', newline='') as csvfile:
                            ErrWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            ErrWriter.writerow([PlaceOrder.json()])

    except (json.decoder.JSONDecodeError, KeyError):
        pass
print(TradedSum)
print("Time at finish for 1130 trades:", datetime.datetime.now())
FinishTime = datetime.datetime.now()
TimeDelta = FinishTime - StartTime

print("Time used for trades:", TimeDelta)
