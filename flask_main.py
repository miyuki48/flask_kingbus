
from functions import startFinalStation as start
from functions.viewSchedule import crawlerScheduleThread
from functions.viewPrice import crawlerTicket
from functions.OrderGo import crawlerOrderGo1,crawlerOrderGo2
from functions.viewOrder import crawlerViewOrder,crawlerViewOrderNum
from functions.OrderCancel import crawlerOrderCancel
from functions.KwTravel import crawlerKwTravel
from flask import Flask, render_template, redirect, request, url_for, jsonify, make_response,session,Response
from flask_mail import Mail, Message
import sqlite3
import pandas as pd
import datetime
import json
import os
import threading
import folium
from werkzeug.security import generate_password_hash, check_password_hash
import string, random



app = Flask(__name__)
app.jinja_env.filters['zip'] = zip

app.secret_key = os.urandom(24) #隨機生成

startStaDict = start.getStartStation()
# print(startStaDict)
    
#heroku(linux環境)檔案讀取不到，將\改為/，出現編碼問題，加上encoding="big5"
with open(r"./functions/startFinalStation.json",encoding="big5") as f:  # 讀取執行startFinalStation.py所產生的json
    data = f.read()
    jsonData = json.loads(data)

# flask_mail 設定
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'flaskjinja23@gmail.com'
app.config['MAIL_PASSWORD'] = 'nbrcwydivescapdu'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#班次查詢
@app.route("/viewSchedule", methods=["GET", "POST"])
def viewSchedule():
    if "logined" in session and session["logined"]=="1": 
        """Embed a map as an iframe on a page."""
        m = folium.Map(location=[23.871390, 120.943787], zoom_start=7)
    
        # set the iframe width and height
        m.get_root().width = "400px"
        m.get_root().height = "500px"
        iframe = m.get_root()._repr_html_()
    
        if request.method == "GET":
            msg = ""
            return render_template("viewSchedule.html", starts=startStaDict, iframe=iframe, msg=msg)
        elif request.method == "POST":
            startStaValue = request.form["startStation"]
            if startStaValue != None: 
                finalStaName = request.form["finalStation"]
    
                # ref: try.py_try2
                startIndex = list(startStaDict.values()).index(startStaValue)
                startStaName = list(startStaDict.keys())[startIndex]
    
                dataList = []
                for i in range(len(jsonData[startIndex][0]["end"])):
                    dataList.append(jsonData[startIndex][0]["end"][i]["finalName"])
                # print(dataList.index("思源警所"))
                # print(jsonData[startIndex][0]["end"][dataList.index(finalSta)]["finalValue"])
                finalStaValue = jsonData[startIndex][0]["end"][dataList.index(finalStaName)]["finalValue"]
    
                startDate = request.form["startDate"]
                finalDate = request.form["finalDate"]
                # print(startStaValue, finalStaValue, startDate)  # A21=板橋 G67=台中 09/12/2023
                # print(type(startStaValue),type(finalStaValue),type(startDate)) #<class 'str'> <class 'str'> <class 'str'>
    
                # 將接收到的日期轉為datetime格式後轉為字串存成list
                date_list = []
                begin_date = datetime.datetime.strptime(startDate, "%m/%d/%Y")
                end_date = datetime.datetime.strptime(finalDate, "%m/%d/%Y")
                while begin_date <= end_date:
                    date_str = begin_date.strftime("%Y/%m/%d")
                    date_list.append(date_str)
                    begin_date += datetime.timedelta(days=1)
                # print(date_list)
                
                if len(date_list) > 2:
                    msg = "請不要選擇超過2天日期!"
                    return render_template("viewSchedule.html", starts=startStaDict, iframe=iframe, msg=msg)
                else:
                    print(startDate,finalDate,date_list,startStaValue,finalStaValue,startStaName,finalStaName)
                    #建立票價比對List
                    ticket = crawlerTicket(startStaValue,finalStaValue,startStaName,finalStaName)
                    ticketCompareList = []
                    for i in range(len(ticket)):
                        compareStr = ticket["起站"][i]+ticket["迄站"][i]+ticket["經由站"][i]+ticket["車種"][i]+","+ticket["全票"][i]+","+ticket["優惠票"][i]
                        ticketCompareList.append(compareStr)
                    # print(ticketCompareList)
                    
                    # 建立 date_list個數 個子執行緒
                    threads = [None] * len(date_list)
                    results = [None] * len(date_list)
                    
                    for i in range(len(date_list)):
                        threads[i] = threading.Thread(target = crawlerScheduleThread, 
                                    args = (startStaValue, finalStaValue, startStaName, 
                                            finalStaName, date_list[i], results, i) )
                        threads[i].start()
        
                    # 等待所有子執行緒結束
                    for i in range(len(date_list)):
                        threads[i].join()
                    
                    schedule = pd.concat(results)
                    schedule.index = [i for i in range(len(schedule))] #將index重新排列    
                    # print(schedule)
                    
                    #班次查詢比對票價查詢，將班次查詢DataFrame加入欄位:全票、優惠票
                    schedule["全票"] = None
                    schedule["優惠票"] = None
                    
                    for i in range(len(schedule)):
                        str1 = schedule["起站"][i]+schedule["迄站"][i]+schedule["經由站"][i]+schedule["車種"][i]
                        # print(str1)
        
                        for j in ticketCompareList:
                            if str1 == j[:len(str1)]:
                                str1 += j[len(str1):]
                                print(str1.split(","))
                                schedule["全票"][i]= str1.split(",")[1]
                                schedule["優惠票"][i] = str1.split(",")[2]
                    
                    #region Description
                    # schedule = crawlerSchedule(
                    #     startStaValue, finalStaValue, startStaName, finalStaName, date_list
                    # )
                    # result = {}
                    # for i in range(len(schedule)):
                    #     result[i] = list(schedule.iloc[i])
        
        
                    # result = {
                    #     "results": [schedule.to_html(classes="data", header="true")],
                    #     "startStaName": startStaName,
                    #     "finalStaName": finalStaName,
                    #     "startDate": startDate,
                    #     "finalDate": finalDate,
                    # }
                    #endregion
                
                    result = {
                        "start":list(schedule["起站"]),
                        "final":list(schedule["迄站"]),
                        "date":list(schedule["乘車日期"]),
                        "time":list(schedule["發車時間"]),
                        "via": list(schedule["經由站"]),
                        "type":list(schedule["車種"]),
                        "price1":list(schedule["全票"]),
                        "price2":list(schedule["優惠票"]),
                        "startStaName": startStaName,
                        "finalStaName": finalStaName,
                        "startDate": startDate,
                        "finalDate": finalDate,
                    }
                    print(result)
                    # return result
                    return render_template("viewScheduleResult.html", result=result, iframe=iframe)
            else:
                msg = ""
                return render_template("viewSchedule.html", starts=startStaDict, iframe=iframe, msg=msg)
    else:
        data = {"user":"","msg":""}
        return render_template('login.html',data=data)
    
    
@app.route("/getSelect", methods=["POST"])
def getSelect():
    startSelect = request.get_json()
    # print(startSelect)

    startName = startSelect["mydata"]
    # print(startName)

    ## 這是先將起迄站爬下來組成json後讀取抓出迄站=>比較快!   ref: try.py_try1
    index = list(startStaDict.keys()).index(startName)

    #region Description
    ##變成全域變數
    # with open(r".\functions\startFinalStation.json") as f: #讀取執行startFinalStation.py所產生的json
    #     data = f.read()
    #     jsonData = json.loads(data)
    #endregion

    FinalNameList = []

    for i in range(len(jsonData[index][0]["end"])):
        FinalNameList.append(jsonData[index][0]["end"][i]["finalName"])

    #region Description
    ## 這是使用者選擇起站後直接去爬迄站=>比較慢!
    # getFinalStation = start.getFinalStation(startStaDict[startName])["end"]
    # print("*****************")
    # print(getFinalStation)
    # print("*****************")

    # FinalNameList = []
    # for i in range(len(getFinalStation)):
    #     FinalNameList.append(getFinalStation[i]["finalName"])
    # print("---------------------")
    # print(FinalNameList)
    #endregion

    print("---------------------")
    return jsonify(FinalNameList)

@app.route('/register',methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        passwordCheck = request.form['passwordCheck']
        name = request.form['name']
        phone = request.form["phone"]
        identity = request.form["identity"]
        email = request.form['email']
        
        #身分證規則檢驗
        rule = {}
        for i in range(65,91):
            rule[chr(i)] = i - 55

        rule["I"] = 34; rule["J"] = 18; rule["K"] = 19; rule["L"] = 20; rule["M"] = 21;
        rule["N"] = 22; rule["O"] = 35; rule["P"] = 23; rule["Q"] = 24; rule["R"] = 25;
        rule["S"] = 26; rule["T"] = 27; rule["U"] = 28; rule["V"] = 29; rule["W"] = 32;
        rule["X"] = 30; rule["Y"] = 31; rule["Z"] = 33;

        numCheck = ((rule[identity[0]] - rule[identity[0]] % 10) / 10) * 1 + (rule[identity[0]] % 10) * 9 + eval(identity[1]) * 8 + \
                    eval(identity[2]) * 7 + eval(identity[3]) * 6 + eval(identity[4]) * 5 + eval(identity[5]) * 4 + \
                    eval(identity[6]) * 3 + eval(identity[7]) * 2 + eval(identity[8]) * 1
        
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select account from  register where account=?;",(user,))
        data = data.fetchone()
        conn.close()
        
        if data != None:
            # print(data)
            msg = "該帳號已註冊，請重新輸入帳號!"
            data =  {"user":user,"name":name,"email":email,"error":msg}
            return  render_template('registerTry.html',data = data)
            
        else:
            if password != passwordCheck:
                    msg = "密碼不一致!"
                    data = {"user":user,"name":name,"email":email,"error":msg}
                    return render_template('registerTry.html',data = data)
            
            else:
                #資料庫
                conn = sqlite3.connect("account.db")
                cursor = conn.cursor()
                #讀取
                data = cursor.execute("select identity from register where identity=?;",(identity,))
                data = data.fetchone()
                conn.close()
                if data != None:
                    msg = "該身份證字號已註冊，請重新輸入身份證字號!"
                    data =  {"user":user,"name":name,"email":email,"error":msg}
                    return  render_template('registerTry.html',data = data)

                else:
                    if (10 - numCheck % 10) % 10 != eval(identity[9]):
                        msg = "身分證字號不符規則!"
                        data = {"user":user,"name":name,"email":email,"error":msg}
                        return  render_template('registerTry.html',data = data)
                    else:
                        #資料庫
                        conn = sqlite3.connect("account.db")
                        cursor = conn.cursor()
                        #讀取
                        data = cursor.execute("select email from  register where email=?;",(email,))
                        data = data.fetchone()
                        conn.close()
                        if data != None:
                            msg = "該email已註冊，請重新輸入email!"
                            data =  {"user":user,"name":name,"email":email,"error":msg}
                            return  render_template('registerTry.html',data = data)

        try:
            vCode = ""
            for i in range(6):
                rand = random.choice(string.ascii_letters)
                vCode += rand
            
            #資料庫
            conn = sqlite3.connect("account.db")
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            # print(user,hashed_password,name,identity,email,datetime.datetime.now(),vCode,"no",datetime.datetime.now()+datetime.timedelta(days=1))
            #寫入
            cursor.execute('''insert into register(account,password,name,phone,identity,email,
                           createTime,verificationCode,verify,verificationTerm) 
                           values(?,?,?,?,?,?,?,?,?,?);''',
                        (user,hashed_password,name,phone,identity,email,datetime.datetime.now(),vCode,"no",datetime.datetime.now()+datetime.timedelta(days=1)))      
            conn.commit()
            # conn.close()
            
            msg = "註冊成功，" +  name + "先生/小姐請登入!"
            data = {"user":user,"msg":msg}
            
            data2 = cursor.execute("select id,name,email,verificationCode,verificationTerm from register where account=?;",(user,))
            data2 = data2.fetchone()
            
            print(data2) #(12, 'happyyyyyyy', 'aaaa@gmail.com', 'cSzLlX', '2023-10-01 19:46:05.963645')
                        
            msg = Message('Hello', sender = 'flaskjinja23@gmail.com', 
                          recipients = [data2[2]])
            msg.body = f'''{data2[1]} 先生/小姐您好，\n以下是您的驗證碼:{data2[3]}\n請盡速於{data2[4][:-7]}前完成認證。'''
            mail.send(msg)
            
            # orderNum = crawlerViewOrderNum(identity,phone)
    
            # #寫入
            # cursor.execute('''insert into customer_order_status(customer_id,bought_num) 
            #                values(?,?);''',(data2[0],orderNum)) 
            # conn.commit()              
            # conn.close()
            
            return render_template('login.html',data = data)
        except:
            conn.rollback()
            conn.close()
            msg ="註冊失敗，請重新註冊!"
            data = {"user":user,"name":name,"email":email,"error":msg}
            return  render_template('registerTry.html',data = data)
            
    elif request.method == 'GET':
        return render_template('register.html')


@app.route('/checkAccount',methods = ['POST'])
def checkAccount():
        user = request.get_data()
        print("!!!!!!!!!!!!!!!!!!!!!!")
        user = user.decode("utf-8") 

        print(user)
    
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select account from  register where account=?;",(user,))
        data = data.fetchone()
        conn.close()
        if data != None:
            # print(data)
            msg = "該帳號已註冊，請重新輸入帳號!"
            return {"msg":msg}
        else:
            # print(data)
            msg = "該帳號沒問題!"
            return {"msg":msg}
        
        
@app.route('/checkId',methods = ['POST'])
def checkId():
        identity = request.get_data()
        print("!!!!!!!!!!!!!!!!!!!!!!")
        identity = identity.decode("utf-8") 

        print(identity)
    
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select identity from  register where identity=?;",(identity,))
        data = data.fetchone()
        if data != None:
            # print(data)
            msg = "該身份證字號已註冊，請重新輸入身份證字號!"
            return {"msg":msg}
        else:
            # print(data)
            msg = "該身份證字號沒問題!"
            return {"msg":msg}
        
        conn.close()
        
@app.route('/checkMail',methods = ['POST'])
def checkMail():
        email = request.get_data()
        print("!!!!!!!!!!!!!!!!!!!!!!")
        email = email.decode("utf-8") 

        print(email)
    
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select email from register where email=?;",(email,))
        data = data.fetchone()
        if data != None:
            # print(data)
            msg = "該email已註冊，請重新輸入email!"
            return {"msg":msg}
        else:
            # print(data)
            msg = "該email沒問題!"
            return {"msg":msg}
        
        conn.close()

@app.route('/',methods = ['POST', 'GET'])
@app.route('/index',methods = ['POST', 'GET'])
def index():
    if "logined" in session and session["logined"]=="1": 
        df = crawlerKwTravel()
        result = {"title":df["title"],"url":df["url"],
                  "price":df["price"],"pic":df["pic"]}
        return render_template('index_logined.html',result=result)
    return render_template('index_logouted.html')


@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']

        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()

        #region Description
        #讀取
        # data = cursor.execute("select account,password from register where account=(?);",(user))
        # '''
        # sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 3 supplied.
        # ref: https://binkery.com/archives/2020.01.03-python-sqlite3-%E5%8F%82%E6%95%B0%E4%B8%AA%E6%95%B0%E9%94%99%E8%AF%AF.html
        # '''   
        #endregion

        data = cursor.execute("select id,name,password,verify,vNewPwdTerm from register where account=?;",(user,))
        data = data.fetchone()
        conn.close()
        
        # check_password = check_password_hash(data[2] ,password)

        # if data[0] == None:  #TypeError: 'NoneType' object is not subscriptable
        if data == None:  
            data = {"user":"","msg":"無此帳號"} 
            return render_template('login.html',data = data)

        elif check_password_hash(data[2] ,password) == False:
            if password == data[2] and datetime.datetime.strptime(data[4][:-7],'%Y-%m-%d %H:%M:%S') > datetime.datetime.now():
                data = {"num":data[0],"msg":"","msgEmail":""}
                return render_template('changePwd.html',data=data)
            
            elif password == data[2]:
                msg = "已過驗證期效，請按下方「寄信」重發暫時性密碼"
                data =  {"error":msg,"user":user}
                return  render_template('forgetPwd.html',data = data)
            
            else:
                data = {"user":user,"msg":"密碼錯誤"} 
                return render_template('login.html',data = data)
        
        else:
            if data[3] == "no":  #verify == "no"
                data = {"name":data[1],"num":data[0],"msg":"","msgEmail":""}
                return render_template('verify.html',data=data)
            else:   
                df = crawlerKwTravel()
                result = {"title":df["title"],"url":df["url"],
                          "price":df["price"],"pic":df["pic"]}
                resp = make_response(render_template('index_logined.html',result=result))
                # resp.set_cookie('num', identity)  # TypeError: Expected bytes
      
                resp.set_cookie('num', str(data[0]), 
                                expires=datetime.datetime.now() + datetime.timedelta(days=30))
                
                '''expires：指定 Cookie的有效日期，當過了有效日期後，那個Cookie就不會再儲存在瀏覽器；
                如果不指定這個參數，該Cookie的有效日期就是使用者退出瀏覽器時。'''
                print(request.cookies.get("num"))
                session['logined'] = "1"
                session.permanent = True  # session設定長期有效，一個月的時間有效
                return resp
    else:
        if "logined" in session and session["logined"]=="1": 
            df = crawlerKwTravel()
            result = {"title":df["title"],"url":df["url"],
                      "price":df["price"],"pic":df["pic"]}
            return render_template('index_logined.html',result=result)
        else:
            data = {"user":"","msg":""}    
            return render_template('login.html',data=data)


@app.route('/verify',methods = ['POST', 'GET'])
def verify():
    if request.method == "POST":
        num = request.form['num']
        name = request.form['name']
        verificationCode = request.form['verificationCode']
        
        print(num,name,verificationCode)
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select verificationCode,verificationTerm from register where id=?;",(num,))
        data = data.fetchone()

        print(data[0])
        term = datetime.datetime.strptime(data[1][:-7],'%Y-%m-%d %H:%M:%S')
        if data[0] == verificationCode and term > datetime.datetime.now():
            #修改成verify='yes'
            cursor.execute("UPDATE register SET verify='yes' WHERE id=?;",(num,))
            conn.commit()
            conn.close()
            
            df = crawlerKwTravel()
            result = {"title":df["title"],"url":df["url"],
                      "price":df["price"],"pic":df["pic"]}
            resp = make_response(render_template('index_logined.html',result=result))
            # resp.set_cookie('num', identity)  # TypeError: Expected bytes
  
            resp.set_cookie('num', num, 
                            expires=datetime.datetime.now() + datetime.timedelta(days=30))
            
            '''expires：指定 Cookie的有效日期，當過了有效日期後，那個Cookie就不會再儲存在瀏覽器；
            如果不指定這個參數，該Cookie的有效日期就是使用者退出瀏覽器時。'''
            print(request.cookies.get('num'))
            session['logined'] = "1"
            session.permanent = True  # session設定長期有效，一個月的時間有效
            return resp
        elif data[0] == verificationCode:
            msg = "已過驗證期效，請按下方重發驗證碼"
            data = {"name":name,"num":num,"msg":msg,"msgEmail":""}
            return  render_template('verify.html',data=data)
        else:
            msg = "驗證失敗，請按下方重發驗證碼或變更信箱"
            data = {"name":name,"num":num,"msg":msg,"msgEmail":""}
            return render_template('verify.html',data=data)

        
@app.route('/sendVcode',methods = ['POST'])
def sendVcode():
    data = request.get_data()
    # print(data)
    data = data.decode("utf-8") 
    # print(data)
    num = data.split("&")[0].split("num=")[1]
    name = data.split("&")[1].split("name=")[1]

    # print(num,name)

    vCode = ""
    for i in range(6):
        rand = random.choice(string.ascii_letters)
        vCode += rand
    #資料庫
    conn = sqlite3.connect("account.db")
    cursor = conn.cursor()
    
    #寫入
    cursor.execute('''UPDATE register SET verificationCode=?,verificationTerm=?
                   WHERE id=?;''',(vCode,datetime.datetime.now()+datetime.timedelta(days=1),num,))
    conn.commit()
    # conn.close()
    
    data = cursor.execute("select name,email,verificationCode,verificationTerm from register where id=?;",(num,))
    data = data.fetchone()
    
    msg = Message('Hello', sender = 'flaskjinja23@gmail.com', 
                  recipients = [data[1]])
    msg.body = f'''{data[0]} 先生/小姐您好，\n以下是您的驗證碼:{data[2]}\n請盡速於{data[3][:-7]}前完成認證。'''
    mail.send(msg)
    
    conn.close()
    return {"ok":"haha"} 


@app.route('/changeEmail',methods = ['POST'])
def changeEmail():
    name = request.form["name"]
    num = request.form["num"]
    email = request.form['newEmail']
    vCode = ""
    for i in range(6):
        rand = random.choice(string.ascii_letters)
        vCode += rand
    #資料庫
    conn = sqlite3.connect("account.db")
    cursor = conn.cursor()
    #讀取
    data = cursor.execute("select email from  register where email=?;",(email,))
    data = data.fetchone()
    conn.close()
    if data != None:
        msgEmail = "該email已註冊，請重新輸入email!"
        data = {"name":name,"num":num,"msg":"","msgEmail":msgEmail}
        return render_template('verify.html',data=data)
    else:
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #寫入
        cursor.execute('''UPDATE register SET email=?,verificationCode=?,verificationTerm=?
                       WHERE id=?;''',(email,vCode,datetime.datetime.now()+datetime.timedelta(days=1),num,))
        conn.commit()
        #讀取
        data = cursor.execute("select name,email,verificationCode,verificationTerm from register where id=?;",(num,))
        data = data.fetchone()
        # print(data) #('sakhas', 'yuki480629@gmail.com', 'QlZdkl')
        msg = Message('Hello', sender = 'flaskjinja23@gmail.com', recipients = [data[1]])
        msg.body = f'''{data[0]} 先生/小姐您好，\n以下是您的驗證碼:{data[2]}\n請盡速於{data[3][:-7]}前完成認證。'''
        mail.send(msg)
        data = {"name":name,"num":num,"msg":"","msgEmail":"變更註冊信箱成功，請至新信箱收取驗證碼!"}
        return render_template('verify.html',data=data)
        
    
@app.route('/logout',methods=['GET','POST'])
def logout ():
    session.pop("logined", None)
    res = Response('delete cookies')
    res.set_cookie(key='num', value='', expires=0)
    return render_template('index_logouted.html')


@app.route('/sendNewPwd',methods = ['GET','POST'])
def sendNewPwd():
    if request.method == 'POST':
        user = request.form["user"]
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()

        #讀取
        data = cursor.execute("select account from register where account=?;",(user,))
        data = data.fetchone()
        conn.close()
        
        if data == None:
            # print(data)
            msg = "該帳號不存在!"
            data =  {"error":msg,"user":""}
            return  render_template('forgetPwd.html',data = data)
        else:
            vPwd = ""
            for i in range(10):   #產生暫時性密碼"123XXXXX"
                rand = random.choice(string.ascii_letters)
                vPwd += rand
            
            #資料庫
            conn = sqlite3.connect("account.db")
            cursor = conn.cursor()
            
            #寫入 vNewPwdTerm=暫時性密碼登入期限
            cursor.execute('''UPDATE register SET password=?,vNewPwdTerm=?
                           WHERE account=?;''',(vPwd,datetime.datetime.now()+datetime.timedelta(hours=1),user,))
            conn.commit()
            
            data = cursor.execute("select name,email,password,vNewPwdTerm from register where account=?;",(user,))
            data = data.fetchone()
            
            msg = Message('Hello', sender = 'flaskjinja23@gmail.com', 
                          recipients = [data[1]])
            msg.body = f'''{data[0]} 先生/小姐您好，\n以下是您的暫時性密碼:{data[2]}\n請盡速於{data[3][:-7]}前登入，盡速完成變更密碼。'''
            mail.send(msg)
            
            conn.close()
            
            msg = "補記密碼成功，" +  data[0] + "先生/小姐請登入!"
            data = {"user":user ,"msg":msg}
            return render_template('login.html',data=data)
    else:
        data =  {"error":"","user":""}
        return  render_template('forgetPwd.html',data = data)

    
@app.route('/ForgetCheckAccount',methods = ['POST'])
def ForgetCheckAccount():
    if request.method == "POST":
        user = request.get_data()
        print("!!!!!!!!!!!!!!!!!!!!!!")
        user = user.decode("utf-8") 

        print(user)
    
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select account from  register where account=?;",(user,))
        data = data.fetchone()
        conn.close()   
        if data != None:
            # print(data)
            msg = "該帳號有存在，沒問題!"
            return {"msg":msg}
        else:
            # print(data)
            msg = "該帳號不存在!"
            return {"msg":msg}
        
        
@app.route('/checkPhone',methods = ['POST'])
def checkPhone():
        data = request.get_data()
        print(data) #b'phone=0954824595&num=2' 
        data = data.decode("utf-8") 
        # print(data)
        num = data.split("&")[1].split("num=")[1]
        phone = data.split("&")[0].split("phone=")[1]
        print(num,phone)
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select phone from register where id=?;",(num,))
        data = data.fetchone()
        print(data) #('0954824597',)
        conn.close()
        if data[0] != phone:
            # print(data)
            msg = "電話輸入錯誤!"
            return {"msg":msg}
        else:
            # print(data)
            msg = "電話輸入正確!"
            return {"msg":msg}
        

@app.route('/changePassword',methods = ['POST',"GET"])
def changePassword():
    if request.method == 'POST':
        num = request.form["num"]
        phone = request.form["phone"]
        newPwd = request.form['newPsd']
        newPwdCheck = request.form["newPwdCheck"]

        hashed_password = generate_password_hash(newPwd)
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select account,phone from  register where id=?;",(num,))
        data = data.fetchone()
        conn.close()
        if data[1] != phone:
            msg = "電話輸入錯誤，請重新輸入電話!"
            data = {"num":num,"msg":msg}
            return render_template('changePwd.html',data=data)
        elif newPwd != newPwdCheck:
            msg = "輸入新密碼不一致!"
            data = {"num":num,"msg":msg}
            return render_template('changePwd.html',data=data)
        else:
            #資料庫
            conn = sqlite3.connect("account.db")
            cursor = conn.cursor()
            #寫入
            cursor.execute('''UPDATE register SET password=? WHERE id=?;''',
                           (hashed_password,num,))
            conn.commit()
            
            data = {"user":data[0],"msg":""}
            return render_template('login.html',data=data)
            

#單程訂票
@app.route("/orderGo", methods=["GET", "POST"])
def orderGo():
    if "logined" in session and session["logined"]=="1":         
        userId = request.cookies.get('num') #取得 cookie
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select identity,phone from register where id=?;",(userId,))
        data = data.fetchone()
        conn.close()
        
        """Embed a map as an iframe on a page."""
        m = folium.Map(location=[23.871390, 120.943787], zoom_start=7)
    
        # set the iframe width and height
        m.get_root().width = "400px"
        m.get_root().height = "500px"
        iframe = m.get_root()._repr_html_()
        
        # hours = [i for i in range(24)]
        # minutes = [i for i in range(0,55,10)]
        
        #把預計搭乘時間送進orderGo.html
        hours,minutes = [],[]

        for i in range(24):
            if i < 10:
                hours.append("0"+str(i))
            else:
                hours.append(str(i))

        for i in range(0,55,10):
            if i < 10:
                minutes.append("0"+str(i))
            else:
                minutes.append(str(i))

        if request.method == "GET":
            data = {"starts":startStaDict, "iframe":iframe,
                    "hours":hours,"minutes":minutes}
            return render_template("orderGo.html", data=data)
        else:
            startStaValue = request.form["startStation"]
            finalStaName = request.form["finalStation"]
            rideDay = request.form["startDate"]  
            hour = request.form["hours"]
            minute = request.form["minutes"]
            # print(startStaValue,finalStaName,rideDay,hours,minutes) #U03 梨山 09/19/2023 18 00
            
            startIndex=list(startStaDict.values()).index(startStaValue)
            startStaName = list(startStaDict.keys())[startIndex]
            
            dataList = []
            for i in range(len(jsonData[startIndex][0]["end"])):
                dataList.append(jsonData[startIndex][0]["end"][i]["finalName"])
        
            finalStaValue = jsonData[startIndex][0]["end"][dataList.index(finalStaName)]["finalValue"]
            # print(startStaName,finalStaValue)  #宜蘭 F14
               
            #將"MM/DD/YYYY"轉為datetime格式YYYY/MM/DD，再轉為字串"YYYY/MM/DD"
            rideDayYMD = datetime.datetime.strptime(rideDay, "%m/%d/%Y").strftime("%Y/%m/%d") 
            print(rideDayYMD)  #2023-09-20 00:00:00
            
            try:
                chooseDf = crawlerOrderGo1(data[0],data[1],startStaValue,finalStaValue,rideDayYMD,hour,minute)
            
                choose = {
                    "start":[startStaName for i in range(len(chooseDf))],
                    "final":[finalStaName for i in range(len(chooseDf))],
                    "date":list(chooseDf["乘車日期"]),
                    "time":list(chooseDf["發車時間"]),
                    "via": list(chooseDf["經由站"]),
                    "type":list(chooseDf["車種"]),
                    "seat":list(chooseDf["剩餘座位數"]),
                    "chooseNum":["one","two","three"]  #選了第[1,2,3]個
                }
                print(choose)
                # return choose
                
                data = {"chooseStart":startStaName,"chooseFinal":finalStaName,
                        "chooseDate":rideDayYMD,"iframe":iframe,"chooseResult":choose,
                        "chooseHour":hour,"chooseMin":minute}
                return render_template("orderGoChoose.html", data=data)
            except:   #當起訖站查不到資料時:訂票未取次數達3次或真的沒有班次資料
                # #資料庫
                # conn = sqlite3.connect("account.db")
                # cursor = conn.cursor()
            
                # #讀取
                # data2 = cursor.execute('''select customer_id,bought_num from customer_order_status
                #                       where customer_id=?;''',(userId,))
                # data2 = data2.fetchone()
                
                orderNum = crawlerViewOrderNum(data[0],data[1])
                
                # if data2[1] >= 3:  #您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票  
                if orderNum >= 3:  #您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票    
                    conn.close()
                    data = {"chooseStart":startStaName,"chooseFinal":finalStaName,
                            "chooseDate":rideDayYMD,"iframe":iframe,
                            "chooseHour":hour,"chooseMin":minute,"msg":"您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票!" }
                    
                    return render_template("orderGoError.html", data=data) #選林口-清大 09/24/2023 07:00
                else:
                    data = {"chooseStart":startStaName,"chooseFinal":finalStaName,
                            "chooseDate":rideDayYMD,"iframe":iframe,
                            "chooseHour":hour,"chooseMin":minute,"msg":"查無資料!" }
                    return render_template("orderGoError.html", data=data) #選林口-清大 09/24/2023 07:00
           
    else:
        data = {"user":"","msg":""}
        return render_template('login.html',data=data)
    
@app.route("/OrderGoBought", methods=["POST"])
def OrderGoBought():
    if "logined" in session and session["logined"]=="1": 
        userId = request.cookies.get('num') #取得 cookie
        
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select identity,phone from register where id=?;",(userId,))
        data = data.fetchone()
        conn.close()
        
        """Embed a map as an iframe on a page."""
        m = folium.Map(location=[23.871390, 120.943787], zoom_start=7)
    
        # set the iframe width and height
        m.get_root().width = "400px"
        m.get_root().height = "500px"
        iframe = m.get_root()._repr_html_()
        
        # hours = [i for i in range(24)]
        # minutes = [i for i in range(0,55,10)]
        
        #把預計搭乘時間送進orderGo.html
        hours,minutes = [],[]

        for i in range(24):
            if i < 10:
                hours.append("0"+str(i))
            else:
                hours.append(str(i))

        for i in range(0,55,10):
            if i < 10:
                minutes.append("0"+str(i))
            else:
                minutes.append(str(i))

        if request.method == "GET":
            data = {"starts":startStaDict, "iframe":iframe,
                    "hours":hours,"minutes":minutes}
            return render_template("orderGo.html", data=data)
        else:
            startStaName = request.form["startStaChoose"]
            finalStaName = request.form["finalStaChoose"]
            rideDayYMDW = request.form["dateChoose"]#ValueError: time data '2023/09/24(日)' does not match format '%m/%d/%Y'
            rideDayYMD = rideDayYMDW[:-3]
            time = request.form["timeChoose"].replace("     ","")
            via = request.form["viaChoose"]
            carType = request.form["typeChoose"]
            residualSeat = request.form["seatChoose"] 
            chooseNumEng = request.form["chooseNum"]  #選了第["one","two","three"]個
            chooseNumDict = {"one":"1","two":"2","three":"3"}
            chooseNum = chooseNumDict[chooseNumEng]
            
            buyChooseTicketNum = request.form["buyChooseTicketNum"] #選了幾張票
            
            chooseHour = request.form["chooseHour"]
            chooseMin = request.form["chooseMin"]
            
            #region Description
            #error
            # if request.form["buyOne"] != None and request.form["buyTwo"] != None and request.form["buyThree"] != None and request.form["buyFour"] != None:
            #     buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
            #     buyThree = request.form["buyThree"];buyFour = request.form["buyFour"];
            #     print(buyOne,buyTwo,buyThree,buyFour)
            # elif request.form["buyOne"] != None and request.form["buyTwo"] != None and request.form["buyThree"] != None:
            #     buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
            #     buyThree = request.form["buyThree"];
            #     print(buyOne,buyTwo,buyThree)
            # elif request.form["buyOne"] != None and request.form["buyTwo"] != None:
            #     buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
            #     print(buyOne,buyTwo)
            # elif request.form["buyOne"] != None:
            #     buyOne = request.form["buyOne"];
            #     print(buyOne)
            #endregion

            print("選了第",chooseNum,"個:",startStaName,finalStaName,rideDayYMDW,time,via,carType,
                  "剩餘座位數:",residualSeat,"購買車票張數:",buyChooseTicketNum)
            #選了第 3 個: 台北轉運 台南 2023/09/22(五) 22:10 林口 國光號 剩餘座位數: 15 購買車票張數: 4
            print(buyChooseTicketNum,type(buyChooseTicketNum)) #<class 'str'>
            
            startStaValue = startStaDict[startStaName]
            startIndex=list(startStaDict.values()).index(startStaValue)
            
            dataList = []
            for i in range(len(jsonData[startIndex][0]["end"])):
                dataList.append(jsonData[startIndex][0]["end"][i]["finalName"])
        
            finalStaValue = jsonData[startIndex][0]["end"][dataList.index(finalStaName)]["finalValue"]
            # print(startStaValue,finalStaValue)  #A03 G67
             
            #參引數設定參考
            #crawlerOrderGo2(identity,phone,startStaValue,finalStaValue,rideDay,hours,mins,chooseNum,buyChooseTicketNum,buyTicketType)
            #crawlerOrderGo2("C199322347","0912345678","A03","G67","2023/09/24","07","30",eval("3"),eval("4"),["5","4","2","1"])
           
            
            try:
                orderNum = crawlerViewOrderNum(data[0],data[1])
                if orderNum < 3:  #您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票
                    if buyChooseTicketNum == "1":
                        buyOne = request.form["buyOne"]
                        print(buyOne)
                        saveDate = crawlerOrderGo2(data[0],data[1],startStaValue,finalStaValue,rideDayYMD,chooseHour,chooseMin,eval(chooseNum),eval(buyChooseTicketNum),[buyOne])
                    elif buyChooseTicketNum == "2":
                        buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
                        print(buyOne,buyTwo)
                        saveDate = crawlerOrderGo2(data[0],data[1],startStaValue,finalStaValue,rideDayYMD,chooseHour,chooseMin,eval(chooseNum),eval(buyChooseTicketNum),[buyOne,buyTwo])
                    elif buyChooseTicketNum == "3":
                        buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
                        buyThree = request.form["buyThree"]
                        print(buyOne,buyTwo,buyThree)
                        saveDate = crawlerOrderGo2(data[0],data[1],startStaValue,finalStaValue,rideDayYMD,chooseHour,chooseMin,eval(chooseNum),eval(buyChooseTicketNum),[buyOne,buyTwo,buyThree])
                    elif buyChooseTicketNum == "4":
                        buyOne = request.form["buyOne"];buyTwo = request.form["buyTwo"];
                        buyThree = request.form["buyThree"];buyFour = request.form["buyFour"];
                        print(buyOne,buyTwo,buyThree,buyFour) #1 2 4 5 
                        saveDate = crawlerOrderGo2(data[0],data[1],startStaValue,finalStaValue,rideDayYMD,chooseHour,chooseMin,eval(chooseNum),eval(buyChooseTicketNum),[buyOne,buyTwo,buyThree,buyFour])
                    
                    print(saveDate) #{'座位號': ['6', '7', '9', '10'], '票種': ['敬老票', '愛心票', '孩童票', '全票'], '總金額': '800'}
                    data = {
                            #訂票結果
                            "rideDayYMDW":rideDayYMDW,"time":time,"via":via,
                            "seatNum":saveDate["座位號"],"ticketType":saveDate["票種"],
                            "orderAmount":saveDate["總金額"],
                            
                            #上方選擇欄
                            "chooseStart":startStaName,"chooseFinal":finalStaName,
                            "chooseDate":rideDayYMD,"chooseHour":chooseHour,"chooseMin":chooseMin,
                            "iframe":iframe
                            }
                    
                    #資料庫
                    conn = sqlite3.connect("account.db")
                    cursor = conn.cursor()
                    #讀取
                    data2 = cursor.execute("select name,email from register where id=?;",(userId,))
                    data2 = data2.fetchone()
                    
                    msg = Message(f'Hello {data2[0]}先生/小姐您好，以下是國光客運訂票資訊', sender = 'flaskjinja23@gmail.com', 
                                  recipients = [data2[1]])
                    msg.body = "訂票結果如下:"
                    msg.html = render_template('orderGoFinishedMail.html',data=data)
                    #ref:https://stackoverflow.com/questions/42136418/send-html-email-using-flask-in-python
                    #ref:https://pythonhosted.org/flask-mail/
                    mail.send(msg)
                    
                    conn.close()
  
                    return render_template('orderGoFinished.html',data=data)
                
                    # #資料庫
                    # conn = sqlite3.connect("account.db")
                    # cursor = conn.cursor()
                    
                    # #讀取
                    # data2 = cursor.execute('''select customer_id,bought_num from customer_order_status
                    #                       where customer_id=?;''',(userId,))
                    # data2 = data2.fetchone()
                    
                  
           
                # if data2[1] < 3:  #您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票
                elif orderNum == 3:  #您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票
                    # #寫入
                    # cursor.execute('''UPDATE customer_order_status SET bought_num=? 
                    #                WHERE customer_id=?;''',(data2[1]+1,userId))
                    # conn.commit()
                    # conn.close()
                    data = {"chooseStart":startStaName,"chooseFinal":finalStaName,
                            "chooseDate":rideDayYMD,"iframe":iframe,"chooseHour":chooseHour,
                            "chooseMin":chooseMin,"msg":"您有尚未取票的訂票次數,最多可訂 3 次,請取票後再訂票!" }
                    return render_template("orderGoError.html", data=data) #選林口-清大 09/24/2023 07:00
          
            except:
                data = {"chooseStart":startStaName,"chooseFinal":finalStaName,
                        "chooseDate":rideDayYMD,"iframe":iframe,"chooseHour":chooseHour,
                        "chooseMin":chooseMin,"msg":"選擇之班次無座位, 請重新選擇！" }
                return render_template("orderGoError.html", data=data) #選林口-清大 09/24/2023 07:00
    else:
        data = {"user":"","msg":""}
        return render_template('login.html',data=data)   

@app.route("/viewOrder", methods=["GET", "POST"])
def viewOrder():
    if "logined" in session and session["logined"]=="1": 
        userId = request.cookies.get('num') #取得 cookie
        
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select identity,phone from register where id=?;",(userId,))
        data = data.fetchone()
        conn.close()
        
        """Embed a map as an iframe on a page."""
        m = folium.Map(location=[23.871390, 120.943787], zoom_start=7)
    
        # set the iframe width and height
        m.get_root().width = "400px"
        m.get_root().height = "500px"
        iframe = m.get_root()._repr_html_()
    
        if request.method == "GET":
            data = {"iframe":iframe,"msg":"",
                    "result":""}
            return render_template("viewOrder.html",data=data)
        elif request.method == "POST":
            result = crawlerViewOrder(data[0],data[1])
            
            if type(result) == str:
                data = {"iframe":iframe,"msg":result,
                        "result":""}
                return render_template("viewOrder.html", data=data)
            else:
                data = {"iframe":iframe,"msg":"",
                        "result":result}
                return render_template("viewOrder.html", data=data)
             
    else:
        data = {"user":"","msg":""}
        return render_template('login.html',data=data)                

@app.route("/orderCancel", methods=["GET", "POST"])
def orderCancel():
    if "logined" in session and session["logined"]=="1": 
        userId = request.cookies.get('num') #取得 cookie
        print(userId)
        #資料庫
        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        #讀取
        data = cursor.execute("select identity,phone from register where id=?;",(userId,))
        data = data.fetchone()
        conn.close()
        print(data[0],data[1])
        """Embed a map as an iframe on a page."""
        m = folium.Map(location=[23.871390, 120.943787], zoom_start=7)
    
        # set the iframe width and height
        m.get_root().width = "400px"
        m.get_root().height = "500px"
        iframe = m.get_root()._repr_html_()
    
        if request.method == "GET":
            data = {"iframe":iframe,"msg":"",
                    "result":""}
            return render_template("viewOrder.html",data=data)
        elif request.method == "POST":
            cancelNum = request.form["cancel"][-1]
            result = crawlerOrderCancel(data[0],data[1],eval(cancelNum))
            data = {"iframe":iframe,"msg":"取消訂票成功!",
                    "result":""}
            # #資料庫
            # conn = sqlite3.connect("account.db")
            # cursor = conn.cursor()
            # #讀取
            # data2 = cursor.execute('''select customer_id,bought_num from customer_order_status
            #                       where customer_id=?;''',(userId,))
            # data2 = data2.fetchone()
            # #寫入
            # cursor.execute('''UPDATE customer_order_status SET bought_num=? 
            #                WHERE customer_id=?;''',(data2[1]-1,userId))
            # conn.commit()
            # conn.close()
            return render_template("viewOrder.html",data=data)
    else:
        data = {"user":"","msg":""}
        return render_template('login.html',data=data) 
    
if __name__ == "__main__":
    # # app.run()
    # app.run(debug=True)
    
    #==============================================
    # #發布heroku
    # port = int(os.environ.get('PORT', 8000))
    # app.run(host='0.0.0.0',debug=False,port=port)
    
    #==============================================
    # ngrok
    app.run(host='0.0.0.0',debug=False,port=5000)
