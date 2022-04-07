import time, json, csv, configparser, requests, datetime, urllib3
import numpy as np
from datetime import date
from datetime import timedelta
import pandas as pd

config = configparser.ConfigParser()
config.read('TOS.ini')

print("time at start for historic analysis:", datetime.datetime.now())
with open('DailyData.csv') as file:
    reader = csv.reader(file)
    factorList = list(reader)

today = date.today()

yesterday = today - timedelta(days=6)
Ystr = yesterday.strftime('%Y-%m-%d')
YOstr = str(Ystr + " 08:30:00")
YEstr = str(Ystr + " 11:30:00")
YLstr = str(Ystr + " 16:00:00")
print(YEstr, YLstr)

StartTime = datetime.datetime.now()
for row in factorList[1:]:
    FList = []
    try:
        #for stock, MetaData in zip(row, row):
        response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + row[0] +
                                "&interval=1min&outputsize=full&apikey=" + config['LoginInfo']['AlphaAPIKey'])
        data = response.json()
        with open('stock_data.json', 'w') as outfile:
            json.dump(data, outfile)
        with open('stock_data.json', 'r') as f:
            PrePreppedData = json.load(f)
        df = pd.DataFrame.from_dict(PrePreppedData['Time Series (1min)'], orient='index')
        MidDayLow = (float(df.loc[YEstr]['1. open']) / float(df.loc[YEstr:YOstr]['3. low'].min())) - 1
        Close1130 = (float(df.loc[YLstr]['4. close']) / float(df.loc[YEstr]['1. open'])) - 1
        MaxProf = (float(df.loc[YLstr:YEstr]['2. high'].max()) / float(df.loc[YEstr]['1. open'])) - 1
        MaxTime = df.loc[YLstr:YEstr]['2. high'].astype(float).idxmax()
        MinTime = df.loc[YLstr:YEstr]['3. low'].astype(float).idxmin()
        BuyPrice = (float(df.loc[MaxTime:YEstr]['3. low'].min()) / float(df.loc[YEstr]['1. open'])) - 1
        FList.append(MidDayLow)
        FList.append(Close1130)
        FList.append(MaxProf)
        FList.append(BuyPrice)
        print(row[0], FList)
        with open('DayTradeStockFactors.csv', 'a', newline='') as csvfile:
            StockWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            StockWriter.writerow([row[0], row[4], FList[0], FList[1], FList[2], FList[3]])
    except KeyError:
        with open('MissedSymbols.csv', 'a', newline='') as csvfile:
            SymWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            SymWriter.writerow([row[0]])
        continue

print("Time at finish for historic analysis:", datetime.datetime.now())
FinishTime = datetime.datetime.now()
TimeDelta = FinishTime - StartTime

print("Time used for historic analysis:", TimeDelta)
