import datetime,calendar
import yfinance as yf 
# https://towardsdatascience.com/financial-data-from-yahoo-finance-with-python-b5399743bcc6
# df = yf.Ticker('2330.TW') # 下載台積電資料
# # print(df.history(period="max"))
# start = datetime.datetime(2021,6,1)
# end = datetime.datetime(2021,7,1)
# print(start,end)
# print(df.history(start=start, end=end))

df = yf.download("2330.TW", start="2021/03/01", end="2021/07/01") 
print(df)