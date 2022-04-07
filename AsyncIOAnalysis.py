import asyncio, configparser, requests, csv, datetime, json
import time
from datetime import date
from datetime import timedelta
import pandas as pd

#symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT']

config = configparser.ConfigParser()
config.read('TOS.ini')

with open('DailyData.csv') as file:
    reader = csv.reader(file)
    symbols = list(reader)

today = date.today()

yesterday = today - timedelta(days=1)
Ystr = yesterday.strftime('%Y-%m-%d')
YOstr = str(Ystr + " 08:30:00")
YEstr = str(Ystr + " 11:30:00")
YLstr = str(Ystr + " 16:00:00")
print(YEstr, YLstr)

StartTime = datetime.datetime.now()

url = "https://alpha-vantage.p.rapidapi.com/query"
FList = []


async def nested(symbol):
    #for stock, MetaData in zip(symbol, symbol):
    querystring = {"symbol": symbol, "function": "TIME_SERIES_INTRADAY", "interval": "15min", "output_size": "full",
                   "datatype": "json"}
    headers = {
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
        'x-rapidapi-key': config['LoginInfo']['x-rapidapi-key']
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    with open('stock_data.json', 'w') as outfile:
        json.dump(data, outfile)
    with open('stock_data.json', 'r') as f:
        PrePreppedData = json.load(f)
    print(PrePreppedData)
    df = pd.DataFrame.from_dict(PrePreppedData['Time Series (15min)'], orient='index')
    print(df.loc[YEstr]['1. open'])

    MidDayLow = (float(df.loc[YEstr]['1. open']) / float(df.loc[YEstr:YOstr]['3. low'].min())) - 1

    Close1130 = (float(df.loc[YLstr]['4. close']) / float(df.loc[YEstr]['1. open'])) - 1
    MaxProf = (float(df.loc[YLstr:YEstr]['2. high'].max()) / float(df.loc[YEstr]['1. open'])) - 1
    MaxTime = df.loc[YLstr:YEstr]['2. high'].astype(float).idxmax()
    MinTime = df.loc[YLstr:YEstr]['3. low'].astype(float).idxmin()
    BuyPrice = (float(df.loc[MaxTime:YEstr]['3. low'].min()) / float(df.loc[YEstr]['1. open'])) - 1
    FList.append(symbol)
    FList.append(MidDayLow)
    FList.append(Close1130)
    FList.append(MaxProf)
    FList.append(BuyPrice)
    print(FList)

    with open('DayTradeStockFactors.csv', 'a', newline='') as csvfile:
        StockWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        StockWriter.writerow([FList[0], FList[1], FList[2], FList[3], FList[4]])
    FList.clear()
    return FList


async def main():
    # Schedule nested() to run soon concurrently
    # with "main()".
    loop = asyncio.get_event_loop()
    tasks = [nested(symbol) for symbol in symbols]
    group1 = asyncio.gather(*tasks)
    results = loop.run_until_complete(group1)
    await tasks
    print(FList)

    loop.close()


print(asyncio.run(main()))

print("Time at finish for historic analysis:", datetime.datetime.now())
FinishTime = datetime.datetime.now()
TimeDelta = FinishTime - StartTime

print("Time used for historic analysis:", TimeDelta)
