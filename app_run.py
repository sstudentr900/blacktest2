# import flask
from flask import  (
    Flask,
    render_template,
    request,
    jsonify,
)
#時間範圍
import datetime,calendar
#用于绘制图表
# import matplotlib.pyplot as plt
#撈股票價格
import pandas_datareader as pdr
#时间序列的计算
import numpy as np
#处理结构化的表格数据
import pandas as pd
import json
# import time

app= Flask(__name__, static_url_path='/static')
app.config['DEBUG'] =True
app.config["JSON_AS_ASCII"] = False

@app.route('/')
def index():
  # ti = pdr.nasdaq_trader.get_nasdaq_symbols()
  ti = '5'
  return render_template('index.html',title=ti) #使用ti變數對應title

@app.route('/backtest',methods=['POST'])
def backtest():
  #撈股票
  # def crawlData(stock,crawlTime):
  def crawlData(stock,timeStart,timeEnd):  
    try:
      #時間範圍
      # cur=datetime.datetime.now() 
      # startYear = cur.year-int(crawlTime)
      # start = datetime.datetime(startYear, cur.month, cur.day)
      # end = datetime.datetime(cur.year, cur.month, cur.day)
      #撈股票價格
      # df = pdr.DataReader(stock+'.TW', 'yahoo', start, end)
      df = pdr.DataReader(stock+'.TW', 'yahoo', timeStart, timeEnd)
      #date
      # df.index = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d %H:%M:%S")) 
      # df['date'] = [datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date() for d in df.index]
      df['date'] = [datetime.datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S") for d in df.index]
      df['date'] = [calendar.timegm(d.utctimetuple())*1000.0 + d.microsecond * 0.0011383651000000 for d in df.date]
      # df['date2'] = [d.strftime("%Y-%m-%d") for d in df.index]
      df.index = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d")) 
      # df['date4'] = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d")) 
      # df.index = df.index.format(formatter=lambda x: x.strftime('%Y-%m-%d')) 
      return df
    except:
      return [] 
  def maLine(obj,json):  
    maDay = int(json['day'])
    maName = str(maDay)+'_day'
    if maName not in obj['df']:
      obj['df'][maName] = np.round(pd.Series(obj['df']['Close'].rolling(window=maDay).mean()),2)
      maData = obj['df'][['date',maName]].dropna().values.tolist()
      maData = {'method':'ma','name':maDay,'data':maData}
      obj['maData'][obj['saletext']].append(maData)
    return maDay,maName,obj
  #price
  def price_increase(obj,json,many_day):
    obj['many_day']=0
    many_day = int(json['many_day'])
    for mi in range(many_day):
      ni = obj['nowIndex']-mi
      close = float(obj['df'].Close[ni])
      close_many = float(obj['df'].Close[ni-1])
      profit,reward = profitFn(close,close_many)
      # print(obj['df'].index[ni],close,reward,json['se'])
      if json['se']=='up':
        if reward >= int(json['number']):
          obj['many_day']+=1
      else:   
        if int(json['number'])*-1 >= reward: 
          obj['many_day']+=1
      # print('price_increase',many_day,mi,ni,reward,int(json['number']),reward >= int(json['number']),obj['many_day'])   
    return obj
  def price(obj,json):
    #連續幾天
    # many_day = 1
    # if json['many']=='y':
    #   many_day = 0
    #   many_day +=int(json['many_day'])
    # if obj['nowIndex'] >= many_day:  
    if json['many']=='y':
      obj['many_day']=0
      many_day = int(json['many_day'])
      for mi in range(many_day):
        ni = obj['nowIndex']-mi
        close = float(obj['df'].Close[ni])
        Open = float(obj['df'].Open[ni])
        profit,reward = profitFn(close,Open)
        if json['se']=='up' and reward >= int(json['number']) or json['se']=='low' and int(json['number'])*-1 >= reward: 
          obj['many_day']+=1
      if many_day == obj['many_day']:
        obj['condition'].append(json)
    if json['many']=='n':   
      ni = obj['nowIndex']
      close = float(obj['df'].Close[ni])
      Open = float(obj['df'].Open[ni])
      profit,reward = profitFn(close,Open)
      print(obj['df'].index[ni],close,Open,reward)
      if json['se']=='up'and reward >= int(json['number']) or json['se']=='low'and int(json['number'])*-1 >= reward:
        obj['condition'].append(json)
      # obj['many_day']=0
      # if json['se']=='up' or json['se']=='low':     
      #   obj=price_increase(obj=obj,json=json,many_day=many_day)
      # if json['se']=='up_l':     
      # if json['se']=='low_l':  
      # if json['se']=='up_h':     
      # if json['se']=='low_h':  
      # print(obj['df'].index[obj['nowIndex']],'條件',json['ch'],json['se'])
      # if many_day==obj['many_day']:
        # print(obj['df'].index[obj['nowIndex']],'條件',json['ch'],json['se'],'true')
        # obj['condition']+=1
    return obj   
  def ma_day(obj,json,maName,ni): 
    close = float(obj['df'].Close[ni])
    close_ma = float(obj['df'][maName][ni])
    if json not in obj['condition']:
      if json['se']=='up'and close >= close_ma or json['se']=='low'and close <= close_ma: 
        obj['condition'].append(json)
    # if json['se']=='up'and close >= close_ma or json['se']=='low'and close <= close_ma: 
    #   obj['many_day']+=1
    return obj     
  def ma(obj,json):
    maDay,maName,obj = maLine(obj=obj,json=json)
    if obj['nowIndex']+1 > maDay:  
      if json['many']=='y':
        obj['many_day']=0
        many_day = int(json['many_day'])
        for mi in range(many_day):
          ni = obj['nowIndex']-mi
          close = float(obj['df'].Close[ni])
          close_ma = float(obj['df'][maName][ni])
          if json['se']=='up'and close >= close_ma or json['se']=='low'and close <= close_ma: 
            obj['many_day']+=1
        if many_day == obj['many_day']:
          obj['condition'].append(json)
      if json['many']=='n':   
        ni = obj['nowIndex']
        close = float(obj['df'].Close[ni])
        close_ma = float(obj['df'][maName][ni])
        # if json not in obj['condition']:
        if json['se']=='up'and close >= close_ma or json['se']=='low'and close <= close_ma: 
          obj['condition'].append(json)
    return obj   
  def column(obj,json):
    ma = int(json['day'])
    text = str(ma)+'_column_day'
    ma2 = int(json['day2'])
    text2 = str(ma2)+'_column_day'
    if text not in obj['df'] or text2 not in obj['df']:
      obj['df'][text] = np.round(pd.Series(obj['df']['Volume'].rolling(window=ma).mean()),2)
      obj['df'][text2] = np.round(pd.Series(obj['df']['Volume'].rolling(window=ma2).mean()),2)
      maData1 = obj['df'][['date',text]].dropna().values.tolist()
      maData2 = obj['df'][['date',text2]].dropna().values.tolist()
      maData3 = obj['df'][['date','Volume']].dropna().values.tolist()
      maDatas = {'method':'column','name':ma,'name2':ma2,'data':{'day1':maData1,'day2':maData2,'column':maData3}}
      obj['maData'][obj['saletext']].append(maDatas)
    if obj['nowIndex']+1 > ma:  
      if json['many']=='y':
        obj['many_day']=0
        many_day = int(json['many_day'])
        for mi in range(many_day):
          ni = obj['nowIndex']-mi
          Volume_ma_l = obj['df'][text][ni]
          Volume_ma_s = obj['df'][text2][ni]
          if json['se']=='up'and Volume_ma_l >= Volume_ma_s or json['se']=='low' and Volume_ma_l <= Volume_ma_s: 
            obj['many_day']+=1
      if json['many']=='n':   
        ni = obj['nowIndex']
        Volume_ma_l = obj['df'][text][ni]
        Volume_ma_s = obj['df'][text2][ni]
        # print('up',Volume_ma_l,Volume_ma_s,json['se']=='up',Volume_ma_l >= Volume_ma_s)
        # print('low',Volume_ma_l,Volume_ma_s,json['se']=='low',Volume_ma_l <= Volume_ma_s)
        if json['se']=='up'and Volume_ma_l >= Volume_ma_s or json['se']=='low' and Volume_ma_l <= Volume_ma_s: 
          # obj['many_day']+=1   
          obj['condition'].append(json)  
    return obj     
  def rsi(obj,json):
    day = int(json['day'])
    value=0
    if 'v' in json:
      value = int(json['v']) 
    rsiTexts = json['day']+'rsi'
    if rsiTexts not in obj['df']:
      def cal_U(num):
        if num >= 0:
            return num
        else:
            return 0
      def cal_D(num):
          num = -num
          return cal_U(num)
      Dif = obj['df']['Close'].diff()
      U = Dif.apply(cal_U)
      D = Dif.apply(cal_D)
      ema_U = U.ewm(span=day).mean()
      ema_D = D.ewm(span=day).mean()
      RS = ema_U.div(ema_D)
      obj['df'][rsiTexts] = round(RS.apply(lambda rs:rs/(1+rs) * 100),2)
      rsiData = obj['df'][['date',rsiTexts]].dropna().values.tolist()
      rsiData = {'method':'rsi','name':day,'data': rsiData}
      obj['maData'][obj['saletext']].append(rsiData)
    if obj['nowIndex'] >= day: 
      #連續幾天
      if json['many']=='y':
        obj['many_day']=0
        many_day = int(json['many_day'])
        for mi in range(many_day):
          ni = obj['nowIndex']-mi
          rsiV = obj['df'][rsiTexts][ni]
          # ni2 = obj['nowIndex']-many_day
          # rsiV2 = obj['df'][rsiTexts][ni2]
          # print(obj['df'].index[i],rsiV,value)
          if json['se']=='up' and rsiV>=value or json['se']=='low' and rsiV<=value:
            obj['many_day']+=1
        if many_day == obj['many_day']:
          obj['condition'].append(json)  
      if json['many']=='n':
        ni = obj['nowIndex']
        rsiV = obj['df'][rsiTexts][ni]
        if json['se']=='up' and rsiV>=value or json['se']=='low' and rsiV<=value:
          obj['condition'].append(json)
    return obj         
  def kd(obj,json):
    value=0
    if 'v' in json:
      value = int(json['v']) 
    day = int(json['day'])
    rsvText = str(day)+'RSV'
    kText = str(day)+'k'
    dText = str(day)+'d'
    if rsvText not in obj['df']:
      # https://medium.com/%E5%8F%B0%E8%82%A1etf%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8-%E7%A8%8B%E5%BC%8F%E9%A1%9E/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80-%E8%87%AA%E5%BB%BAkd%E5%80%BC-819d6fd707c8
      #一、 要算出KD值，必先算出RSV強弱值，以下以 9 天為計算基準。
      #RSV=( 收盤 - 9日內的最低 ) / ( 9日內的最高 - 9日內的最低 ) * 100
      #二、 再以平滑移動平均法，來計算KD值。
      #期初：K= 50，D= 50
      #當日K值=前一日K值 * 2/3 + 當日RSV * 1/3
      #當日D值=前一日D值 * 2/3 + 當日K值 * 1/3 
      # print('Close11',type(obj['df']['Close']),obj['df']['Close'])
      # rsv =(obj['df']['Close'])*100
      rsv =(obj['df']['Close']-obj['df']['Close'].rolling(window=day).min())/(obj['df']['Close'].rolling(window=day).max()-obj['df']['Close'].rolling(window=day).min())*100
      #把前8筆NaN改為0
      rsv = np.nan_to_num(rsv)
      #資料放入dataframe裡
      RSV=pd.DataFrame(rsv)
      #名稱定義為RSV
      RSV.columns = [rsvText]
      #索引比照收盤價以日期為主
      RSV.index=obj['df']['Close'].index
      #把新創的RSV欄位放入df的RSV欄位
      obj['df'][rsvText] = RSV[rsvText]
      #創建K值 給前8筆(k1)一個初始值a
      k1 = []
      for a in range(day):
          a = 0
          k1.append(a)
      k1=pd.DataFrame(k1)
      k1.columns = [kText]  
      #第9筆之後就可以開始計算
      k2 = []
      k_temp = a
      for i in range(len(obj['df'])-day):
        #當日K值=前一日K值 * 2/3 + 當日RSV * 1/3
        k_temp = k_temp*2/3+obj['df'][rsvText][i+day]*(1/3)
        k2.append(round(k_temp,1))
      k2=pd.DataFrame(k2)
      k2.columns = [kText]
      K = pd.concat([k1,k2])
      K.index=obj['df']['Close'].index
      obj['df'][kText] = K[kText]
      #創建D值
      d1 = []
      for b in range(day):
          b = 0
          d1.append(b)
      d1=pd.DataFrame(d1)
      d1.columns = [dText]
      d2 = []
      d_temp = b
      for j in range(len(obj['df'])-day):
          #當日D值=前一日D值 * 2/3 + 當日K值 * 1/3
          d_temp = d_temp*2/3+obj['df'][kText][j+day]*(1/3)
          d2.append(round(d_temp,1))
      d2=pd.DataFrame(d2)
      d2.columns = [dText]
      D = pd.concat([d1,d2])
      D.index=obj['df']['Close'].index
      obj['df'][dText] = D[dText]
      # print(obj['df'].head(20))
      maDataK = obj['df'][['date',kText]].dropna().values.tolist()
      maDataD = obj['df'][['date',dText]].dropna().values.tolist()
      maData = {'method':'kd','name':day,'data':{'k':maDataK,'d':maDataD}}
      obj['maData'][obj['saletext']].append(maData)
    if obj['nowIndex'] >= day:  
      #連續幾天
      if json['many']=='y':
        obj['many_day']=0
        many_day = int(json['many_day'])
        for mi in range(many_day):
          ni = obj['nowIndex']-mi
          kTextV = obj['df'][kText][ni]
          dTextV = obj['df'][dText][ni]
          # ni2 = obj['nowIndex']-many_day
          # kTextV2 = obj['df'][kText][ni2]
          # dTextV2 = obj['df'][dText][ni2]
          if json['se']=='up' and kTextV>=value or json['se']=='low' and kTextV<=value or json['se']=='up_d' and kTextV>=dTextV or json['se']=='low_d' and kTextV<=dTextV:
            obj['many_day']+=1   
            # print('234','day',day,json['many'],obj['df'].index[obj['nowIndex']],obj['saletext'],json['ch'],kTextV,json['se'],dTextV,kTextV2,dTextV2)  
        if many_day == obj['many_day']:
          obj['condition'].append(json)    
      #不連續幾天      
      if json['many']=='n':
        ni = obj['nowIndex']
        kTextV = obj['df'][kText][ni]
        dTextV = obj['df'][dText][ni]
        if json['se']=='up'and kTextV>=value or json['se']=='low' and kTextV<=value or json['se']=='up_d' and kTextV>=dTextV or json['se']=='low_d' and kTextV<=dTextV:
          obj['condition'].append(json) 
    return obj     
  #profitFn
  def profitFn(close,close2):
    profit = round(float(close)-float(close2),2)
    reward = round((profit/float(close2))*100,2)
    profit = round(profit*1000,0)
    return profit,reward
  def tableDataAdd(obj,buyText='買',buyText2='1張',nowProfit=0,nowReward=0,profit=0,reward=0):
    # print('nowIndex',type(obj['df'].Close[obj['nowIndex']]))
    stock = obj['stock']
    date = obj['df'].index[obj['nowIndex']]
    buySheets = buyText+buyText2+' / '+str(obj['buySheets'])
    price = '%.2f'%obj['df'].Close[obj['nowIndex']]
    average = '%.2f'%obj['average']
    nowReward = str(nowReward)+'%'
    reward = str(reward)+'%'
    obj['tableData'].append([stock,date,buySheets,price,average,nowProfit,nowReward,profit,reward])
    obj['flagsData'][obj['saletext']].append({'x':obj['df'].date[obj['nowIndex']],'title':buyText+'%.2f'%obj['df'].Close[obj['nowIndex']]})
    return obj  
  def sellMethod(obj,buyText2='1張',profit=0,reward=0):
    # 日期不同天
    if obj['tableData'][-1][1]!=obj['df'].index[obj['nowIndex']]:
      nowClose = obj['df']['Close'][obj['nowIndex']]
      #交易成本
      # buySheets = obj['buySheets']+1
      # nowClose= nowClose-((obj['average']*0.001425)+(nowClose*0.001425)+(nowClose*0.003))
      # print('281',nowClose,obj['average'])
      profit,reward=profitFn(close=nowClose,close2=obj['average'])  
      # profit = profit*(obj['buySheets']+1)
      profit = profit*(obj['buySheets'])
      # reward = reward-0.585
      obj['buySheets']-=1
      obj['sellPrice'].append(profit)
      obj['sellPlay'].append(reward)
      obj['buySheets']=0 
      obj['average']=0
      obj['bulls']=[]
      obj = tableDataAdd(obj=obj,buyText='賣',buyText2=buyText2,profit=profit,reward=reward)  
    #買賣條件都成立就取消  
    # print( len(obj['tableData']),obj['tableData'][-1][1],obj['df'].index[obj['nowIndex']])  
    # if len(obj['tableData']) and obj['tableData'][-1][1]==obj['df'].index[obj['nowIndex']]:  
    #   if obj['json']['buyMethod']=='1':
    #     obj['tableData'].pop()
    #     obj['flagsData']['buy'].pop()
    #     obj['average']=0
    #     obj['bulls']=[]
    #     if obj['buySheets']!=0:
    #       obj['buySheets']-=1 
    # else:
    #   obj = tableDataAdd(obj=obj,buyText='賣',buyText2=buyText2,profit=profit,reward=reward)  
    return obj
  def saleConfirm(obj):
    # 符和條件
    # if len(obj['json'][obj['saletext']])==obj['condition']:
    if obj['json'][obj['saletext']]==obj['condition']:  

      #買入方式1
      if obj['json']['buyMethod']=='1':
        if obj['saletext']=='buy':
          obj['buySheets']+=1
          obj['average']= obj['df']['Close'][obj['nowIndex']]
          obj =tableDataAdd(obj=obj)  
          # obj=buyMethod(obj=obj)    
        if obj['saletext']=='sell':
          obj=sellMethod(obj=obj)

      #買入方式2
      if obj['json']['buyMethod']=='2': 
        if obj['saletext']=='buy':
          obj['buySheets']+=1
          nowProfit=0
          nowReward=0
          obj['bulls'].append(obj['df']['Close'][obj['nowIndex']])
          if len(obj['tableData'])==0:
            # obj['average'] = round(obj['df'].Close[obj['nowIndex']],2)
            obj['average'] =obj['df'].Close[obj['nowIndex']]
            # print('329', obj['average'])
          else:
            # print('331','buy2',obj['bulls'],len(obj['bulls']),round(float(sum(obj['bulls']))/len(obj['bulls']),2))
            obj['average'] = round(float(sum(obj['bulls']))/len(obj['bulls']),2)
            nowProfit,nowReward=profitFn(close=obj['df']['Close'][obj['nowIndex']],close2=obj['average']) 
            # print(obj['bulls'],obj['buySheets'])
            nowProfit = nowProfit*obj['buySheets']
          obj=tableDataAdd(obj=obj,nowProfit=nowProfit,nowReward=nowReward)    
        if obj['saletext']=='sell': 
          # print('338','sell',obj['average'])
          # obj['buySheets']-=1
          obj=sellMethod(obj=obj,buyText2='全部')
      
      #買入方式3
      # if obj['json']['buyMethod']=='3': 
      #   if obj['saletext']=='buy':
      #     obj['bulls'].append(obj['df']['Close'][obj['nowIndex']])
      #     if len(obj['tableData'])==0:
      #       # nowAverage = obj['df'].Close[obj['nowIndex']]  
      #       obj['average'] = obj['df'].Close[obj['nowIndex']]
      #     else:
      #       # nowAverage = round(float(sum(obj['bulls']))/len(obj['bulls']),2)
      #       obj['average'] = round((obj['average']+obj['df']['Close'][obj['nowIndex']])/2,2)
      #       nowProfit,nowReward=profitFn(close=obj['df']['Close'][obj['nowIndex']],close2=obj['average']) 
      #       nowProfit = nowProfit*obj['buySheets']
      #     obj=tableDataAdd(obj=obj,buyText='買',buyText2='1張',nowProfit=nowProfit,nowReward=nowReward)    
      #   if obj['saletext']=='sell':    
      #     if obj['tableData'][-1][1]!=obj['df'].index[obj['nowIndex']]:
      #       # nowAverage = round(float(sum(obj['bulls']))/len(obj['bulls']),2)
      #       profit,reward=profitFn(close=obj['df']['Close'][obj['nowIndex']],close2=obj['average']) 
      #       profit = profit*(obj['buySheets']+1)
      #       obj['sellPrice'].append(profit)
      #       obj['sellPlay'].append(reward)
      #       nowProfit,nowReward=profitFn(close=obj['df']['Close'][obj['nowIndex']],close2=obj['average']) 
      #       nowProfit = nowProfit*obj['buySheets']
    return obj
  #saleFn
  def saleFn(obj):
    obj['condition']=[]
    for json in obj['json'][obj['saletext']]:
      if json['ch']=='kd':
        obj = kd(obj=obj,json=json)
      if json['ch']=='rsi':
        obj = rsi(obj=obj,json=json)
      if json['ch']=='ma':
        obj = ma(obj=obj,json=json)
      if json['ch']=='price':
        obj = price(obj=obj,json=json)
      if json['ch']=='column':
        obj = column(obj=obj,json=json)  
    return saleConfirm(obj) 
  #jsonData
  def jsonData(obj):
    jsonValue = jsonify({"result": 'false','errorInfo':'找不到買賣點!!'})
    if len(obj['flagsData']['buy']):
      #最後一筆是買
      obj['buyPrice'] = 0
      obj['buyPlay'] = 0
      if obj['nowIndex']+1==len(obj['df']) and obj['average']!=0:
        oldProfit,oldReward=profitFn(close=obj['df']['Close'][i],close2=obj['average']) 
        obj['buyPrice'] = oldProfit*obj['buySheets']
        obj['buyPlay'] = round(oldReward,2)
      buyPrice =  obj['buyPrice']
      buyPlay = obj['buyPlay']
      sellPrice = sum(obj['sellPrice'])
      sellPlay = sum(obj['sellPlay'])
      totlePrice = buyPrice+sellPrice
      totlePlay = buyPlay+sellPlay
      obj['tableData'].append(['庫存總損益 : %d元'%buyPrice,'庫存總報酬 : %.2f'%buyPlay+'%','賣出總損益 : %d元'%sellPrice,'賣出總報酬 : %.2f'%sellPlay+'%','總損益 : %d元'%totlePrice,'總報酬 : %.2f'%totlePlay+' %'])
      jsonValue = jsonify({
        "result": 'true',
        "table": obj['tableData'],
        "imgPoints": {
          'close':obj['df'][['date','Open','High','Low','Close']].dropna().values.tolist(),
          'flags':obj['flagsData'],
          'buy':obj['maData']['buy'],
          'sell':obj['maData']['sell']
          }
      })
    return jsonValue
  

  obj={
    'buySheets':0,
    'tableData':[],
    'flagsData':{'buy':[],'sell':[]},
    'maData':{'buy':[],'sell':[]},
    'buyPlay':[],
    'buyPrice':[],
    'sellPlay':[],
    'sellPrice':[],
    'totlePlay':[],
    'totlePrice':[],
    'bulls':[],
    'json':json.loads(request.get_data()), # json
    'df':[],
    'stock':0,
    'average':0,
    'many_day':0,
    'condition':0,
    'saletext':'buy',
    'nowIndex':0,
  }
  # df=crawlData(stock=obj['json']['stock'],crawlTime=obj['json']['time'])
  df=crawlData(stock=obj['json']['stock'],timeStart=obj['json']['timeStart'],timeEnd=obj['json']['timeEnd'])
  jsonValue = jsonify({"result": 'false','errorInfo':'找不到資料'})  
  if len(df):
    obj['df']= df
    obj['stock']=obj['json']['stock']
    for i in range(0,len(df)):
      obj['nowIndex']=i
      # print('568',obj['df'].index[i],obj['saletext'])
      if obj['buySheets']==0 or obj['json']['buyMethod']=='2' or obj['json']['buyMethod']=='3':
        obj['saletext']='buy'
        obj=saleFn(obj)
      if obj['buySheets']>0:
        obj['saletext']='sell'
        obj=saleFn(obj)
    jsonValue = jsonData(obj)   
  return jsonValue



if __name__ == '__main__':
  app.run(debug=True)
