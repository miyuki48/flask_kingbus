
from bs4 import BeautifulSoup
# import pandas as pd
import requests
from selenium import webdriver #載入 webdriver 模組
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys 
from time import sleep
# import threading
# import sqlite3
# import datetime
# import re
# import sqlite3

import os
from selenium.webdriver.chrome.service import Service

def crawlerViewOrder(identity,phone):
    url = "https://order.kingbus.com.tw/ORD/ORD_M_1540_ViewOrder.aspx"
    my_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    
    session = requests.Session()
    # session.proxies = {"https":"431b-49-216-177-130.ngrok-free.app"}
    resp = session.get(url,headers = my_header)
    
    outsideList = []
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,"html.parser")
        # print(soup.title)
        a__VIEWSTATE = soup.select_one("input#__VIEWSTATE").get("value")
        a__VIEWSTATEGENERATOR = soup.select_one("input#__VIEWSTATEGENERATOR").get("value")
    
        paylaod = {
                "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$updStep1|ctl00$ContentPlaceHolder1$btnQuery",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "", 
                "__LASTFOCUS": "",
                "__VIEWSTATE": a__VIEWSTATE,
                "__VIEWSTATEGENERATOR": a__VIEWSTATEGENERATOR,
                "ctl00$hLanguage": "zh-TW",
                "ctl00$rdoLanguage": "zh-TW",
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtTarget": "", 
                "ctl00$ContentPlaceHolder1$txtCustomer_ID": identity,
                "ctl00$ContentPlaceHolder1$txtPhone": phone,
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtTitle": "Message",
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtMsg": "查無資料!",
                "__ASYNCPOST": "true",
                "ctl00$ContentPlaceHolder1$btnQuery": "查詢"
                }
        resp = session.post(url,data = paylaod,headers = my_header)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text,"html.parser")
            targets = soup.select("#ctl00_ContentPlaceHolder1_grdOrderList td")
            
            if targets == []:
                msg = "查無未取票之訂票資訊"
                return msg
            else:
                if len(targets)//7 == 1:
                    dataDict = {}
                    orderNumList = []  #訂單編號
                    orderedDateList = []  #訂票日期
                    orderAmountList = []  #金額
                    goOrGobackList = []  #單/去回程
                    payMethodList = [] #付款方式
                    payStateList = []  #付款狀態
                    
                    rideDayList = []  #乘車日期
                    rideTimeList = []  #乘車時間
                    startFinalViaList = []  #起迄站(經由站)
                    carTypeList = []  #車種
                    seatNumList = []  #座位號
                    
                    for orderNum,orderedDate,orderAmount,goOrGoback,payMethod,payState in zip(targets[1],targets[2],targets[3],targets[4],targets[5],targets[6]):
                        dataDict["訂單編號"] = orderNum.text
                        dataDict["訂票日期"] = orderedDate.text
                        dataDict["金額"] = orderAmount.text
                        dataDict["單/去回程"] = goOrGoback.text
                        dataDict["付款方式"] = payMethod.text
                        dataDict["付款狀態"] = payState.text
                        
                    targets2 = soup.select("#ctl00_ContentPlaceHolder1_grdList td")
                    for j in range(len(targets2)//5):
                        for rideDay,rideTime,startFinalVia,carType,seatNum in zip(targets2[0+5*j],targets2[1+5*j],targets2[2+5*j],targets2[3+5*j],targets2[4+5*j]):
                            rideDayList.append(rideDay.text)
                            rideTimeList.append(rideTime.text.replace("     ",""))
                            startFinalViaList.append(startFinalVia.text.replace("　　",""))
                            carTypeList.append(carType.text)
                            seatNumList.append(seatNum.text)
                    
                    dataDict["詳細訂單資訊"] = {"乘車日期":rideDayList,"乘車時間":rideTimeList,
                                              "起迄站(經由站)":startFinalViaList,"車種":carTypeList,
                                              "座位號":seatNumList}   
                    outsideList.append(dataDict)
                    return outsideList

                elif len(targets)//7 != 1:
                    #=============================================================
                    # # heroku:selenium無頭模式+linux環境設定
                    # chrome_options = webdriver.ChromeOptions()
                    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                    # chrome_options.add_argument("--headless") #無頭模式
                    # chrome_options.add_argument("--disable-dev-shm-usage")
                    # chrome_options.add_argument("--no-sandbox")
                    # service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
                    # driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                    
                    # #windows環境設定
                    # s = webdriver.chrome.service.Service(r'./chromedriver.exe')
                    # driver=webdriver.Chrome(service=s) #建立瀏覽器物件
                    
                    #ngrok轉址
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--headless") #無頭模式
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--no-sandbox")
                    s = webdriver.chrome.service.Service(r'./chromedriver.exe')
                    driver=webdriver.Chrome(service=s, options=chrome_options) #建立瀏覽器物件
                    #=============================================================
                    
                    driver.get(url) 
                    
                    #輸入步驟一：輸入身份證號之身份證號
                    driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtCustomer_ID').send_keys(identity)
                    #輸入步驟一：輸入身份證號之聯絡電話
                    driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtPhone').send_keys(phone)
                    #點選步驟一：輸入身份證號查詢按鈕
                    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnQuery").click()   
                    #顯性等待步驟二：訂票記錄出現
                    WebDriverWait(driver, 5, 0.1).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_lblOrderStatus')))
                    
                    for i in range(len(targets)//7):
                        dataDict = {}
                        orderNumList = []  #訂單編號
                        orderedDateList = []  #訂票日期
                        orderAmountList = []  #金額
                        goOrGobackList = []  #單/去回程
                        payMethodList = [] #付款方式
                        payStateList = []  #付款狀態
                        
                        rideDayList = []  #乘車日期
                        rideTimeList = []  #乘車時間
                        startFinalViaList = []  #起迄站(經由站)
                        carTypeList = []  #車種
                        seatNumList = []  #座位號
                        
                    
                        for orderNum,orderedDate,orderAmount,goOrGoback,payMethod,payState in zip(targets[1+7*i],targets[2+7*i],targets[3+7*i],targets[4+7*i],targets[5+7*i],targets[6+7*i]):
                            dataDict["訂單編號"] = orderNum.text
                            dataDict["訂票日期"] = orderedDate.text
                            dataDict["金額"] = orderAmount.text
                            dataDict["單/去回程"] = goOrGoback.text
                            dataDict["付款方式"] = payMethod.text
                            dataDict["付款狀態"] = payState.text
                        
                        #點選步驟二：訂票記錄選擇按鈕
                        ##ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child(2) > td:nth-child(1) > input[type=button]
                        ##ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child(3) > td:nth-child(1) > input[type=button]
                        driver.find_element(By.CSS_SELECTOR, f"#ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child({i+2}) > td:nth-child(1) > input[type=button]").click()   
                        #顯性等待第二個表格出現
                        WebDriverWait(driver, 5, 0.1).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_grdList')))
                        sleep(1) #因為太快了，BeautifulSoup解析只會抓到第一個，所以睡個1秒
                        
                        soup = BeautifulSoup(driver.page_source,"html.parser")
                        targets = soup.select("#ctl00_ContentPlaceHolder1_grdOrderList td")
                        targets2 = soup.select("#ctl00_ContentPlaceHolder1_grdList td")
                        # print(targets2)
                        
                        for j in range(len(targets2)//5):
                            for rideDay,rideTime,startFinalVia,carType,seatNum in zip(targets2[0+5*j],targets2[1+5*j],targets2[2+5*j],targets2[3+5*j],targets2[4+5*j]):
                                rideDayList.append(rideDay.text)
                                rideTimeList.append(rideTime.text.replace("     ",""))
                                startFinalViaList.append(startFinalVia.text.replace("　　","").replace("　",""))
                                carTypeList.append(carType.text)
                                seatNumList.append(seatNum.text)
                                
                        dataDict["詳細訂單資訊"] = {"乘車日期":rideDayList,"乘車時間":rideTimeList,
                                                  "起迄站(經由站)":startFinalViaList,"車種":carTypeList,
                                                  "座位號":seatNumList}   

                        outsideList.append(dataDict)   
                    return outsideList
                            
                    driver.quit() # 關閉chromedriver.exe

def crawlerViewOrderNum(identity,phone):
    url = "https://order.kingbus.com.tw/ORD/ORD_M_1540_ViewOrder.aspx"
    my_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    
    session = requests.Session()
    resp = session.get(url,headers = my_header)
    
    outsideList = []
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,"html.parser")
        # print(soup.title)
        a__VIEWSTATE = soup.select_one("input#__VIEWSTATE").get("value")
        a__VIEWSTATEGENERATOR = soup.select_one("input#__VIEWSTATEGENERATOR").get("value")
    
        paylaod = {
                "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$updStep1|ctl00$ContentPlaceHolder1$btnQuery",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "", 
                "__LASTFOCUS": "",
                "__VIEWSTATE": a__VIEWSTATE,
                "__VIEWSTATEGENERATOR": a__VIEWSTATEGENERATOR,
                "ctl00$hLanguage": "zh-TW",
                "ctl00$rdoLanguage": "zh-TW",
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtTarget": "", 
                "ctl00$ContentPlaceHolder1$txtCustomer_ID": identity,
                "ctl00$ContentPlaceHolder1$txtPhone": phone,
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtTitle": "Message",
                "ctl00$ContentPlaceHolder1$UsrMsgBox$txtMsg": "查無資料!",
                "__ASYNCPOST": "true",
                "ctl00$ContentPlaceHolder1$btnQuery": "查詢"
                }
        resp = session.post(url,data = paylaod,headers = my_header)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text,"html.parser")
            targets = soup.select("#ctl00_ContentPlaceHolder1_grdOrderList td")
            
            if targets == []:
                num = 0
                return num
            elif len(targets)//7 == 1:
                num = 1
                return num
            elif len(targets)//7 == 2:
                num = 2
                return num
            elif len(targets)//7 == 3:
                num = 3
                return num

if __name__ == "__main__":
    saveList = crawlerViewOrder("D286479938","0987654321")
    num = crawlerViewOrderNum("D286479938","0987654321")
