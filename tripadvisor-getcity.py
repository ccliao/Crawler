import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
from random import randint
from time import sleep
import csv

#取得一階城市名單
def getcity1():
    r = requests.get('https://www.tripadvisor.com.tw/MapPopup?geo=294232')
    soup = bs(r.text,'lxml')
    bs_city = soup.select('map area')
    city_url,city_name,city_area,sight_url = [],[],[],[]

    for i in range(len(bs_city)):
        if i%2 == 0:
            pass
        else:
            city_url.append(bs_city[i]['href'].split("\'")[1])
            city_name.append(bs_city[i]['alt'])
            if bs_city[i]['alt'].strip() == "北海道":
                city_area.append('')
                sight_url.append('https://www.tripadvisor.com.tw/Attractions-g298143-Activities-Hokkaido.html')
            else:
                city_area.append(re.split('[\- \_]', bs_city[i]['href'])[4])
                a = re.split('\-', bs_city[i]['href'])[1]
                b = re.split('\-', bs_city[i]['href'])[2]
                sight_url.append('https://www.tripadvisor.com.tw/Attractions-'+a+'-Activities-'+b+'.html')

    city_1_list = pd.DataFrame({'cityname':city_name, 'cityurl':city_url, 'cityarea':city_area, 'sighturl':sight_url})
    return sight_url

#取得二階城市名單
def getcity2(sighturl):
#     sighturl = 'https://www.tripadvisor.com.tw/Attractions-g298103-Activities-Aichi_Prefecture_Chubu.html'
    re =requests.get(sighturl, headers = headers)
    soup = bs(re.text,'lxml')
    clist = soup.select('#CHILD_GEO_FILTER .al_border a')

    clist_name,clist_url = [],[]
    for i in range(len(clist)):
        if clist[i].text.split('的')[0] != "更多":
            clist_name.append(clist[i].text.split('的')[0])
            clist_url.append('https://www.tripadvisor.com.tw'+clist[i].get('href'))
        else:
            url = 'https://www.tripadvisor.com.tw'+clist[i].get('href')
            re =requests.get(url, headers = headers)
            soup = bs(re.text,'lxml')
            clist_more = soup.select('#LOCATION_LIST .geoList a')
            for i in range(len(clist_more)):
                clist_name.append(clist_more[i].text.replace('景點', ''))
                clist_url.append('https://www.tripadvisor.com.tw'+clist_more[i].get('href'))

    city_2_list = pd.DataFrame({'clist_name':clist_name, 'clist_url':clist_url})
    if not os.path.isfile("japncitylist.csv"):
        city_2_list.to_csv("japncitylist.csv")
    else:
        city_2_list.to_csv("japncitylist.csv", mode='a', header=False)

#其實只要sight_url及clist_url,而clist_url用於取景點資料
#取得二階城市連結網址
if __name__ == '__main__':
    sight_url = getcity1()
    for i in sight_url:
        print (i)
        getcity2(i)
        sleep(randint(1,5))
    print ('Finished')