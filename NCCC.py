import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import os
from flask import session
from time import sleep
from random import randint
import datetime

#讀取帳號密碼
with open('nccc.txt', 'r') as nccc_account:
    ac = nccc_account.readlines()
    for i in ac:
        OfficeCode = i.split()[0]
        LoginId = i.split()[1]
        Passwd = i.split()[2]
        print (LoginId+"開始處理")
               
        url = "https://inquiry.nccc.com.tw/NASApp/NTC/servlet/com.du.mvc.EntryServlet"

        with requests.session() as s:
            #登入帳號密碼
            postData = {
                'Action': "Authenticate",
                'UserType': "6",
                'CounterName': "Shop",
                'OfficeCode' : OfficeCode,
                'LoginId' : LoginId,
                'Passwd' : Passwd
            }
            try:
                sleep(randint(1,5))
                s.post(url, data = postData, timeout=10)
                print ('登入帳號')
                cookies = ''.join([s.cookies.keys()[0],'=',s.cookies.values()[0]])
            except requests.exceptions.Timeout:
                print ("Timeout occurred")

            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
                'Accept-Encoding': 'gzip, deflate, br',
                'Host': 'inquiry.nccc.com.tw',
                'Referer': 'https://inquiry.nccc.com.tw/html/index_shop.htm',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '108',
                'Cookie': cookies,
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
                
            #查詢資料
            if OfficeCode == '8071210':
                LoginId = '807'+LoginId+'0001'
            payload = {
                'Action':'BookList',
                'Type':'Read',
                'AcqFID':OfficeCode,
                'RetlID':LoginId,
                'CardNo':'',
                'BeginDateYY':'2016',
                'BeginDateMM':'1',
                'BeginDateDD':'1',
                'EndDateYY':'2017',
                'EndDateMM':'12',
                'EndDateDD':'31',
                'RequestType':'2'
            }
            try:
                sleep(randint(1,5))
                res = s.post(url, data = payload, timeout=10, headers = headers)
                print ('查詢資料')
            except requests.exceptions.Timeout:
                print ("Timeout occurred")
       
        s.cookies.clear()
        print ('清除cookies')
        
        #讀取資料
        res.encoding = 'big5'
        soup = bs(res.text,'lxml')
        if soup.select('table'):
            tb = soup.select('table')[0]
            cr_data = pd.read_html(tb.prettify('utf-8'),encoding='utf-8', header = 0)[0]
            print ('讀取資料')

            #寫入資料
            savefilename = "Taiwan_Traveler_Card_" + datetime.datetime.now().strftime('%Y%m%d') + ".csv"
            if not os.path.isfile(savefilename):
                cr_data.to_csv(savefilename, index = False)
            else:
                cr_data.to_csv(savefilename, mode='a', header=False, index = False)

        #完成時列印帳號
        print (LoginId+"處理結束")
nccc_account.close()