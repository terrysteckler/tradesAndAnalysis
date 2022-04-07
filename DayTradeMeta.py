import csv
import pandas as pd

df = pd.read_csv('DayTradeStockFactors.csv')

Close1130 = df.Close1130.mean()

C1130Std = df.Close1130.std()
MaxProf = df.MaxProf.mean()
ProfMedian = df.MaxProf.median()
MPStd = df.MaxProf.std()
BuyPrice = df.BuyPrice.mean()
BPStd = df.BuyPrice.std()
MidDayLow = df.MidDayLow.mean()
print('Profit:', MaxProf, 'MPStdDev:', MPStd, 'Buy Price:', BuyPrice, 'BPStd:', BPStd, 'Close1130', Close1130,
      'C1130Std:', Close1130, "MidDayLow:", MidDayLow)
BPM = df.BuyPrice.median()

with open('DayTradeStockFactors.csv') as file:
    reader = csv.reader(file)
    factorList = list(reader)

MedList = []
ClBuyList = []
for row in factorList[1:]:
    Cl1130 = float(row[3])

    BPF = float(row[5])
    MP = float(row[4])
    if BPF < BPM:
        #print(Cl1130/(1-BPM))
        MedList.append((1+float(row[4]))/(1+BPM))
        ClBuyList.append(1+float(row[3])/1+BPM)
df2 = pd.DataFrame(MedList, columns=['Meds'])
MeanSub = df2.Meds.mean()
StdSub = df2.Meds.std()
MedSub = df2.Meds.median()

df3 = pd.DataFrame(ClBuyList, columns=['ClBuy'])
ClBuyMeanSub = df3.ClBuy.mean()
ClBuyStdSub = df3.ClBuy.std()
ClBuyMedSub = df3.ClBuy.median()


print('Buy Price Median:', BPM, 'Median Profit:', ProfMedian, 'Subset Mean:',
      MeanSub, 'Subset Std Dev:', StdSub, 'Subset Median:', MedSub, 'Close/Buy Median:',
      ClBuyMedSub, 'Close/Buy Std:', ClBuyStdSub, 'Close/Buy Mean:', ClBuyMeanSub)

with open('DayTradeStockMetaFactors.csv', 'a', newline='') as csvfile:
    StockWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    StockWriter.writerow([Close1130, C1130Std, MaxProf, ProfMedian, MPStd, BuyPrice,
                          BPStd, MidDayLow, BPM, MeanSub, StdSub, MedSub, ClBuyMeanSub, ClBuyStdSub, ClBuyMedSub])
