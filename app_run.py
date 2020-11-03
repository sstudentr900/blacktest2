# import flask
from flask import  (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    make_response,
)
# from flask_cors import CORS
import json
from datetime import datetime
from fun.custom import (
  # crawlData,
  # jsonData,
  # saleFn,
  index_send_Fn,
)

import psycopg2
conn=psycopg2.connect(database='ddfcmko4fd6ghb',user='mcaeityvstcljq',password='72964581f46309cce56e649677be3c0148e1ee7d86b5d0d9901dca9c4f251988',host='ec2-34-232-24-202.compute-1.amazonaws.com',port='5432')
cur = conn.cursor()


#布林
#macd
#抓出前高前低
#全買全賣，獲利就買就賣
#排名，id
#優先

app= Flask(__name__, static_url_path='/static')
app.config['DEBUG'] =True #是否開始除錯模式
app.config["JSON_AS_ASCII"] = False
# CORS(app) 

@app.route('/about')
def about():
  return render_template("about.html")
#ranking  
@app.route('/ranking')
def ranking():
  sql = "SELECT * FROM public.rank ORDER BY id ASC" 
  cur.execute(sql)
  count = cur.rowcount #查找到數量
  jsonValue = ''
  if count>=1:
    jsonValue = cur.fetchall()
  return render_template('ranking.html',jsonvalue=jsonValue) 
@app.route('/ranking_delet',methods=['POST'])
def ranking_delet():
  data = json.loads(request.get_data())
  # print(data)
  sql = "SELECT id FROM public.use WHERE id=1 AND password='%s'" % (data['passwor'])
  cur.execute(sql)
  count = cur.rowcount #查找到數量
  jsonValue = jsonify({'result': 'false','message':'密碼錯誤'})   
  if count>=1:
    # print(data,data['id'])
    sql="DELETE FROM public.rank WHERE id=%s" % (data['id'])
    cur.execute(sql)
    conn.commit()
    jsonValue = jsonify({'result': 'true'}) 
  return jsonValue   
#index 
@app.route('/')
def index():
  jsonValue=''
  return render_template('index.html',jsonvalue= jsonValue)
@app.route("/<int:id>", methods=['GET'])
def index_id(id):
  sql = "SELECT conditions FROM public.rank WHERE id=%d" % (id)
  cur.execute(sql)
  count = cur.rowcount #查找到數量
  if count>=1:
    dataValue = cur.fetchone()[0]
    jsonValue = index_send_Fn(jsons=dataValue)
    jsonValue['stock'] = dataValue['stock']
    jsonValue['buyMethod'] = dataValue['buyMethod']
    jsonValue['timeStart'] = dataValue['timeStart']
    jsonValue['timeEnd'] = dataValue['timeEnd']
    jsonValue['formBuy'] = dataValue['buy']
    jsonValue['formSell'] = dataValue['sell']
    return render_template('index.html',jsonvalue= jsonValue)
  else:
    return redirect(url_for('index'))
@app.route("/bargain/<int:id>", methods=['GET'])
def bargain(id):
  sql = "SELECT conditions FROM public.rank WHERE id=%d" % (id)
  cur.execute(sql)
  count = cur.rowcount #查找到數量
  jsonValue = jsonify({'result': False,'messae':'找不到資料'}) 
  if count>=1:
    dataValue = cur.fetchone()[0]
    todayTime = datetime.today().strftime("%Y/%m/%d")
    dataValue['timeEnd']= todayTime
    jsonValue = index_send_Fn(jsons=dataValue)
    buyDatas = jsonValue['imgPoints']['flags']['buy'].pop()
    sellDatas = jsonValue['imgPoints']['flags']['sell'].pop()
    buyTime = datetime.utcfromtimestamp(float(buyDatas['x'])/1000.0).strftime('%Y/%m/%d')
    sellTime = datetime.utcfromtimestamp(float(sellDatas['x'])/1000.0).strftime('%Y/%m/%d')
    text = '股號:%s;日期:%s;%s' % (dataValue['stock'],todayTime,'今天沒有買賣點')
    if todayTime == buyTime:
        text = '股號:%s;日期:%s;建議可%s' % (dataValue['stock'],todayTime,buyDatas['title'])
    if todayTime == sellTime:
        text = '股號:%s;日期:%s;建議可%s' % (dataValue['stock'],todayTime,sellDatas['title'])
    # print(buyTime,sellTime,todayTime)
    jsonValue = jsonify({'result': True,'message':text}) 
  return jsonValue
@app.route('/index_save',methods=['POST'])
def index_save():
  data = json.loads(request.get_data())
  sql = '''INSERT INTO public.rank (conditions) VALUES ('%s')''' % json.dumps(data)
  cur.execute(sql)
  conn.commit()
  jsonValue = jsonify({'result': 'true'}) 
  return jsonValue
@app.route('/index_send',methods=['POST'])
def index_send():
  dataValue = json.loads(request.get_data())
  return jsonify(index_send_Fn(jsons=dataValue))

if __name__ == '__main__':
  app.run(debug=True)
