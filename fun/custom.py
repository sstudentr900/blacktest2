# # import flask
# from flask import  (
#     jsonify,
# )
#時間範圍
import datetime,calendar
#撈股票價格
import pandas_datareader as pdr
# #时间序列的计算
import numpy as np
# #处理结构化的表格数据
import pandas as pd
#撈股票
def crawlData(stock, timeStart, timeEnd):
    try:
        #時間範圍
        # cur=datetime.datetime.now()
        # startYear = cur.year-int(crawlTime)
        # start = datetime.datetime(startYear, cur.month, cur.day)
        # end = datetime.datetime(cur.year, cur.month, cur.day)
        #撈股票價格
        # df = pdr.DataReader(stock+'.TW', 'yahoo', start, end)
        df = pdr.DataReader(stock + '.TW', 'yahoo', timeStart, timeEnd)
        #date
        # df.index = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        # df['date'] = [datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date() for d in df.index]
        df['date'] = [
            datetime.datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S")
            for d in df.index
        ]
        df['date'] = [
            calendar.timegm(d.utctimetuple()) * 1000.0 +
            d.microsecond * 0.0011383651000000 for d in df.date
        ]
        # df['date2'] = [d.strftime("%Y-%m-%d") for d in df.index]
        df.index = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d"))
        # df['date4'] = df.index.format(formatter=lambda x: x.strftime("%Y-%m-%d"))
        # df.index = df.index.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
        return df
    except:
        return []
def maLine(obj, day):
    maDay = int(day)
    maName = str(maDay) + '_day'
    if maName not in obj['df']:
        obj['df'][maName] = np.round(
            pd.Series(obj['df']['Close'].rolling(window=maDay).mean()), 2)
        maData = obj['df'][['date', maName]].dropna().values.tolist()
        maData = {'method': 'ma', 'name': maDay, 'data': maData}
        # obj['maData'][obj['saletext']].append(maData)
        obj['linegraph'].append(maData)
    return maDay, maName, obj
def profitFn(close, close2):
    profit = round(float(close) - float(close2), 2)
    reward = round((profit / float(close2)) * 100, 2)
    profit = round(profit * 1000, 0)
    return profit, reward    
def se_fn(json,l=0,s=0,l2=0,s2=0):
    result = False
    if json['se'] == 'up' and l >= s or json['se'] == 'low' and l <= s:
        if l2!=0 and s2!=0:
            if json['se'] == 'up' and l2 <= s2 or json['se'] == 'low' and l2 >= s2:
                result=True
        else:
            result=True        
    return result     
def many_fn(obj,json,ma,vv,vt):   
    ni = obj['nowIndex']  
    if ni + 1 > ma:
        obj['many_day'] = 0
        many_day = 1
        #連續天數
        if json['many'] == 'y':
            many_day = int(json['many_day'])
        for mi in range(many_day):
            ni2 = ni - mi
            l = float(vv[ni2])
            s = float(vt[ni2])
            l2 = 0
            s2 = 0
            #起漲
            if json['rise']=='y':
                ni3 = ni - many_day
                l2 = float(vv[ni3])
                s2 = float(vt[ni3])
            if se_fn(json=json,l=l,s=s,l2=l2,s2=s2):
                obj['many_day'] += 1
        #是否符合        
        if many_day == obj['many_day']:
            obj['condition'].append(json)
    return obj            
def ma(obj, json):
    #建立均線
    day = int(json['day'])
    ma, text, obj = maLine(obj=obj, day=day)
    day2 = int(json['day2'])
    ma2, text2, obj = maLine(obj=obj, day=day2)
    #大於均線天數
    vv = obj['df'][text]
    vt = obj['df'][text2]
    return many_fn(obj=obj,json=json,ma=ma,vv=vv,vt=vt)
def price(obj, json):
    #建立均線
    day = int(json['day'])
    ma, text, obj = maLine(obj=obj, day=day)
    #大於均線天數
    # ni = obj['nowIndex']
    vv = obj['df'].Close
    vt = obj['df'][text]
    return many_fn(obj=obj,json=json,ma=ma,vv=vv,vt=vt)
def price2(obj, json):
    # reply = False
    if json['many'] == 'y':
        obj['many_day'] = 0
        many_day = int(json['many_day'])
        for mi in range(many_day):
            ni = obj['nowIndex'] - mi
            close = float(obj['df'].Close[ni])
            Open = float(obj['df'].Open[ni])
            profit, reward = profitFn(close, Open)
            if json['se'] == 'up' and reward >= int(json['number']) or json['se'] == 'low' and int(json['number']) * -1 >= reward:
                obj['many_day'] += 1
        if many_day == obj['many_day']:
            # reply = True
            obj['condition'].append(json)
    if json['many'] == 'n':
        ni = obj['nowIndex']
        close = float(obj['df'].Close[ni])
        Open = float(obj['df'].Open[ni])
        profit, reward = profitFn(close, Open)
        if json['se'] == 'up' and reward >= int(json['number']) or json['se'] == 'low' and int(json['number']) * -1 >= reward:
            # reply = True
            obj['condition'].append(json)
    # #非優先    
    # if reply:
    #     obj['condition'].append(json)        
    return obj    
def column_maData(obj,maTexts):
    for v in maTexts: 
        text = v['text'] 
        ma = v['ma']    
        if text not in obj['df']:
            obj['df'][text] = np.round(pd.Series(obj['df']['Volume'].rolling(window=ma).mean()), 2)
            datas={
                'day': obj['df'][['date', text]].dropna().values.tolist(),
                'name': ma
            }
            maData_bool = True
            maData_id=0
            # for i,v in enumerate(obj['maData'][obj['saletext']]):
            # for i,v in enumerate(obj['maData']['buy']):   
            for i,v in enumerate(obj['linegraph']):         
                if v['method']=='column':
                    maData_bool = False
                    maData_id = i
            if maData_bool:
                maDatas = {
                    'method': 'column',
                    'column':  obj['df'][['date', 'Volume']].dropna().values.tolist(),
                    'data':[]
                } 
                maDatas['data'].append(datas)
                # obj['maData'][obj['saletext']].append(maDatas)   
                # obj['maData']['buy'].append(maDatas)
                obj['linegraph'].append(maDatas)
                
            else:
                # obj['maData'][obj['saletext']][maData_id]['data'].append(datas)
                # obj['maData']['buy'][maData_id]['data'].append(datas)
                obj['linegraph'][maData_id]['data'].append(datas)
    return obj     
def column(obj, json):
    ma = int(json['day'])
    text = str(ma) + '_column_day'
    maTexts = [{'ma': ma,'text':text}]
    obj = column_maData(obj=obj,maTexts=maTexts)
    # ni = obj['nowIndex']
    vv = obj['df']['Volume']
    vt = obj['df'][text]
    return many_fn(obj=obj,json=json,ma=ma,vv=vv,vt=vt)
def column2(obj, json):
    ma = int(json['day'])
    text = str(ma) + '_column_day'
    ma2 = int(json['day2'])
    text2 = str(ma2) + '_column_day'
    maTexts = [{'ma':ma,'text':text},{'ma':ma2,'text':text2}]
    obj = column_maData(obj=obj,maTexts=maTexts)
    # ni = obj['nowIndex']
    vv = obj['df'][text]
    vt = obj['df'][text2]
    return many_fn(obj=obj,json=json,ma=ma,vv=vv,vt=vt)
def rsi(obj, json):
    day = int(json['day'])
    rsiTexts = json['day'] + 'rsi'
    rsiValue = json['day'] + 'value'
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
        obj['df'][rsiTexts] = round(RS.apply(lambda rs: rs / (1 + rs) * 100),2)
        obj['df'][rsiValue] = int(json['v'])
        rsiData = obj['df'][['date', rsiTexts]].dropna().values.tolist()
        rsiData = {'method': 'rsi', 'name': day, 'data': rsiData}
        # obj['maData'][obj['saletext']].append(rsiData)
        obj['linegraph'].append(rsiData)
    vv = obj['df'][rsiTexts]
    vt = obj['df'][rsiValue]
    return many_fn(obj=obj,json=json,ma=day,vv=vv,vt=vt)
def kd(obj, json):
    value = 0
    reply = False
    if 'v' in json:
        value = int(json['v'])
    day = int(json['day'])
    rsvText = str(day) + 'RSV'
    kText = str(day) + 'k'
    dText = str(day) + 'd'
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
        rsv = (obj['df']['Close'] -
               obj['df']['Close'].rolling(window=day).min()) / (
                   obj['df']['Close'].rolling(window=day).max() -
                   obj['df']['Close'].rolling(window=day).min()) * 100
        #把前8筆NaN改為0
        rsv = np.nan_to_num(rsv)
        #資料放入dataframe裡
        RSV = pd.DataFrame(rsv)
        #名稱定義為RSV
        RSV.columns = [rsvText]
        #索引比照收盤價以日期為主
        RSV.index = obj['df']['Close'].index
        #把新創的RSV欄位放入df的RSV欄位
        obj['df'][rsvText] = RSV[rsvText]
        #創建K值 給前8筆(k1)一個初始值a
        k1 = []
        for a in range(day):
            a = 0
            k1.append(a)
        k1 = pd.DataFrame(k1)
        k1.columns = [kText]
        #第9筆之後就可以開始計算
        k2 = []
        k_temp = a
        for i in range(len(obj['df']) - day):
            #當日K值=前一日K值 * 2/3 + 當日RSV * 1/3
            k_temp = k_temp * 2 / 3 + obj['df'][rsvText][i + day] * (1 / 3)
            k2.append(round(k_temp, 1))
        k2 = pd.DataFrame(k2)
        k2.columns = [kText]
        K = pd.concat([k1, k2])
        K.index = obj['df']['Close'].index
        obj['df'][kText] = K[kText]
        #創建D值
        d1 = []
        for b in range(day):
            b = 0
            d1.append(b)
        d1 = pd.DataFrame(d1)
        d1.columns = [dText]
        d2 = []
        d_temp = b
        for j in range(len(obj['df']) - day):
            #當日D值=前一日D值 * 2/3 + 當日K值 * 1/3
            d_temp = d_temp * 2 / 3 + obj['df'][kText][j + day] * (1 / 3)
            d2.append(round(d_temp, 1))
        d2 = pd.DataFrame(d2)
        d2.columns = [dText]
        D = pd.concat([d1, d2])
        D.index = obj['df']['Close'].index
        obj['df'][dText] = D[dText]
        # print(obj['df'].head(20))
        maDataK = obj['df'][['date', kText]].dropna().values.tolist()
        maDataD = obj['df'][['date', dText]].dropna().values.tolist()
        maData = {
            'method': 'kd',
            'name': day,
            'data': {
                'k': maDataK,
                'd': maDataD
            }
        }
        # obj['maData'][obj['saletext']].append(maData)
        obj['linegraph'].append(maData)
    if obj['nowIndex'] >= day:
        #連續幾天
        if json['many'] == 'y':
            obj['many_day'] = 0
            many_day = int(json['many_day'])
            for mi in range(many_day):
                ni = obj['nowIndex'] - mi
                kTextV = obj['df'][kText][ni]
                dTextV = obj['df'][dText][ni]
                if json['se'] == 'up' and kTextV >= value or json['se'] == 'low' and kTextV <= value or json['se']=='up_d' and kTextV >= dTextV or json['se'] == 'low_d' and kTextV <= dTextV:
                    #起漲點
                    if json['rise']=='y':
                        ni2 = obj['nowIndex']-many_day
                        kTextV2 = obj['df'][kText][ni2]
                        dTextV2 = obj['df'][dText][ni2]
                        if json['se'] == 'up' and kTextV2 <= value or json['se'] == 'low' and kTextV2 >= value or json['se'] == 'up_d' and kTextV2 <= dTextV2 or json['se'] == 'low_d' and kTextV2 >= dTextV2:
                            obj['many_day'] += 1
                    else:     
                        obj['many_day'] += 1
            if many_day == obj['many_day']:
                reply = True
                # obj['condition'].append(json)
        #不連續幾天
        if json['many'] == 'n':
            ni = obj['nowIndex']
            kTextV = obj['df'][kText][ni]
            dTextV = obj['df'][dText][ni]
            if json['se'] == 'up' and kTextV >= value or json[ 'se'] == 'low' and kTextV <= value or json['se'] == 'up_d' and kTextV >= dTextV or json['se'] == 'low_d' and kTextV <= dTextV:
                #起漲點
                if json['rise']=='y':
                    ni2 = obj['nowIndex']-1
                    kTextV2 = obj['df'][kText][ni2]
                    dTextV2 = obj['df'][dText][ni2]
                    if json['se'] == 'up' and kTextV2 <= value or json['se'] == 'low' and kTextV2 >= value or json['se'] == 'up_d' and kTextV2 <= dTextV2 or json['se'] == 'low_d' and kTextV2 >= dTextV2:
                        reply = True
                        # obj['condition'].append(json)
                else: 
                    reply = True    
                    # obj['condition'].append(json)
        #非優先    
        if reply:
        # if reply or json['need']=='n':
            obj['condition'].append(json)

    return obj
def tableDataAdd(obj,
                 buyText='買',
                 buyText2='1張',
                 nowProfit=0,
                 nowReward=0,
                 profit=0,
                 reward=0):
    # print('nowIndex',type(obj['df'].Close[obj['nowIndex']]))
    stock = obj['stock']
    date = obj['df'].index[obj['nowIndex']]
    buySheets = buyText + buyText2 + ' / ' + str(obj['buySheets'])
    price = '%.2f' % obj['df'].Close[obj['nowIndex']]
    average = '%.2f' % obj['average']
    nowReward = str(nowReward) + '%'
    reward = str(reward) + '%'
    obj['tableData'].append([
        stock, date, buySheets, price, average, nowProfit, nowReward, profit,
        reward
    ])
    obj['flagsData'][obj['saletext']].append({
        'x':
        obj['df'].date[obj['nowIndex']],
        'title':
        buyText + '%.2f' % obj['df'].Close[obj['nowIndex']]
    })
    return obj
def sellMethod(obj, buyText2='1張', profit=0, reward=0):
    # 日期不同天
    if obj['tableData'][-1][1] != obj['df'].index[obj['nowIndex']]:
        nowClose = obj['df']['Close'][obj['nowIndex']]
        #交易成本
        # buySheets = obj['buySheets']+1
        # nowClose= nowClose-((obj['average']*0.001425)+(nowClose*0.001425)+(nowClose*0.003))
        # print('281',nowClose,obj['average'])
        profit, reward = profitFn(close=nowClose, close2=obj['average'])
        # profit = profit*(obj['buySheets']+1)
        profit = profit * (obj['buySheets'])
        # reward = reward-0.585
        obj['buySheets'] -= 1
        obj['sellPrice'].append(profit)
        obj['sellPlay'].append(reward)
        obj['buySheets'] = 0
        obj['average'] = 0
        obj['bulls'] = []
        obj = tableDataAdd(obj=obj,
                           buyText='賣',
                           buyText2=buyText2,
                           profit=profit,
                           reward=reward)
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
    if obj['json'][obj['saletext']] == obj['condition']:

        #買入方式1
        if obj['json']['buyMethod'] == '1':
            if obj['saletext'] == 'buy':
                obj['buySheets'] += 1
                obj['average'] = obj['df']['Close'][obj['nowIndex']]
                obj = tableDataAdd(obj=obj)
                # obj=buyMethod(obj=obj)
            if obj['saletext'] == 'sell':
                obj = sellMethod(obj=obj)

        #買入方式2
        if obj['json']['buyMethod'] == '2':
            if obj['saletext'] == 'buy':
                obj['buySheets'] += 1
                nowProfit = 0
                nowReward = 0
                obj['bulls'].append(obj['df']['Close'][obj['nowIndex']])
                if len(obj['tableData']) == 0:
                    # obj['average'] = round(obj['df'].Close[obj['nowIndex']],2)
                    obj['average'] = obj['df'].Close[obj['nowIndex']]
                    # print('329', obj['average'])
                else:
                    # print('331','buy2',obj['bulls'],len(obj['bulls']),round(float(sum(obj['bulls']))/len(obj['bulls']),2))
                    obj['average'] = round(
                        float(sum(obj['bulls'])) / len(obj['bulls']), 2)
                    nowProfit, nowReward = profitFn(
                        close=obj['df']['Close'][obj['nowIndex']],
                        close2=obj['average'])
                    # print(obj['bulls'],obj['buySheets'])
                    nowProfit = nowProfit * obj['buySheets']
                obj = tableDataAdd(obj=obj,nowProfit=nowProfit,nowReward=nowReward)
            if obj['saletext'] == 'sell':
                # print('338','sell',obj['average'])
                # obj['buySheets']-=1
                obj = sellMethod(obj=obj, buyText2='全部')

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
#買賣
def saleFn(obj):
    obj['condition'] = []
    commands = {
        'kd': kd,
        'rsi': rsi,
        'price': price,
        'price2': price2,
        'column': column,
        'column2': column2,
        'ma': ma,
    }
    for json in obj['json'][obj['saletext']]:
        if json['ch'] in commands:
            func = commands[json['ch']]
            obj = func(obj=obj, json=json)
    return saleConfirm(obj)
#json
def jsonData(obj):
    jsonValue = {'result': 'false', 'errorInfo': '找不到買賣點!!'}
    if len(obj['flagsData']['buy']):
        #最後一筆是買
        obj['buyPrice'] = 0
        obj['buyPlay'] = 0
        if obj['nowIndex'] + 1 == len(obj['df']):
            if obj['average'] != 0:
                oldProfit, oldReward = profitFn(close=obj['df']['Close'][obj['nowIndex']],close2=obj['average'])
                obj['buyPrice'] = oldProfit * obj['buySheets']
                obj['buyPlay'] = round(oldReward, 2)
            buyPrice = obj['buyPrice']
            buyPlay = obj['buyPlay']
            sellPrice = sum(obj['sellPrice'])
            sellPlay = sum(obj['sellPlay'])
            totlePrice = buyPrice + sellPrice
            totlePlay = buyPlay + sellPlay
            obj['tableData'].append([
                '庫存總損益 : %d元' % buyPrice,
                '庫存總報酬 : %.2f' % buyPlay + '%',
                '賣出總損益 : %d元' % sellPrice,
                '賣出總報酬 : %.2f' % sellPlay + '%',
                '總損益 : %d元' % totlePrice,
                '總報酬 : %.2f' % totlePlay + ' %'
            ])
        jsonValue = {
            'result': 'true',
            'table': obj['tableData'],
            'imgPoints': {
                'close':obj['df'][['date', 'Open', 'High', 'Low','Close']].dropna().values.tolist(),
                'flags':obj['flagsData'],
                'linegraph':obj['linegraph'],
                # 'buy':
                # obj['maData']['buy'],
                # 'sell':
                # obj['maData']['sell']
            }
        }
    return jsonValue
def index_send_Fn(jsons):
    jsonValue = {'result': 'false','errorInfo':'找不到資料'}
    obj= {
        'buySheets':0,
        'tableData':[],
        'flagsData':{'buy':[],'sell':[]},
        # 'maData':{'buy':[],'sell':[]},
        'linegraph':[],
        'buyPlay':[],
        'buyPrice':[],
        'sellPlay':[],
        'sellPrice':[],
        'totlePlay':[],
        'totlePrice':[],
        'bulls':[],
        'json': 0,
        'df':[],
        'stock':0,
        'average':0,
        'many_day':0,
        'condition':0,
        'saletext':'buy',
        'nowIndex':0,
    }
    # print('550',jsons)
    obj['json'] = jsons
    # print('552',obj['json'])
    df=crawlData(stock=obj['json']['stock'],timeStart=obj['json']['timeStart'],timeEnd=obj['json']['timeEnd'])
    if len(df):
        obj['df']= df
        obj['stock']=obj['json']['stock']
        for i in range(0,len(df)):
            obj['nowIndex']=i
            # print('sell' not in obj['json'])
            if obj['buySheets']==0 or obj['json']['buyMethod']=='2':
                obj['saletext']='buy'
                obj=saleFn(obj)
            if obj['buySheets']>0 and 'sell' in obj['json']:
                obj['saletext']='sell'
                obj=saleFn(obj)
        jsonValue = jsonData(obj)   
    return jsonValue    