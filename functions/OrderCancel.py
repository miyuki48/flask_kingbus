
# from bs4 import BeautifulSoup
# import pandas as pd
# import requests
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

def crawlerOrderCancel(identity,phone,cancelNum):
    url = "https://order.kingbus.com.tw/ORD/ORD_Q_1550_OrderCancel.aspx"
    
    #region Description
    #=============================================================
    # # heroku:selenium無頭模式+linux環境設定
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_options.add_argument("--headless") #無頭模式
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # #endregion
    
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
    
    try:
        try:  #當可以取消訂票只有1筆訂單時走這邊
            #顯性等待步驟二：詳細訂單確定取消按鈕出現
            WebDriverWait(driver, 3, 0.1).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_btnCancel')))
            
            #點選步驟二：詳細訂單內容確定取消按鈕
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnCancel").click()   
            
            driver.quit() # 關閉chromedriver.exe
        except:  #當可以取消訂票不只有1筆訂單時走這邊
            #顯性等待步驟二：詳細訂單內容出現
            WebDriverWait(driver, 3, 0.1).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_pnlStep2')))
            
            ##ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child(2) > td:nth-child(1) > input[type=button]
            ##ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child(3) > td:nth-child(1) > input[type=button]
            ##ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child(4) > td:nth-child(1) > input[type=button]
            #點選步驟二：訂票記錄選取按鈕
            driver.find_element(By.CSS_SELECTOR, f"#ctl00_ContentPlaceHolder1_grdOrderList > tbody > tr:nth-child({cancelNum+1}) > td:nth-child(1) > input[type=button]").click()   
            sleep(1)
            
            #點選步驟二：訂票記錄下一步按鈕
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnNext").click()   
            #顯性等待步驟二：詳細訂單確定取消按鈕出現
            WebDriverWait(driver, 3, 0.1).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_btnCancel')))
            
            #點選步驟二：詳細訂單內容確定取消按鈕
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnCancel").click()
            
            driver.quit() # 關閉chromedriver.exe
    except:    
        driver.quit() # 關閉chromedriver.exe
        print("此身分證號查無未結案之訂票資訊。")
        
                    
if __name__ == "__main__":
    saveData = crawlerOrderCancel("D286479938","0987654321",1)        
    

