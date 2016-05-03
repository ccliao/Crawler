import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
from random import randint
from time import sleep
import csv

headers = {
'X-Requested-With':'XMLHttpRequest',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
}

def getattraction(area, city_1_en, city_2_en, soup):
    attname, attname_url, rank, spec, score, comment_count, comment_url = [],[],[],[],[],[],[]

    for j in range(len(soup.select('.property_title a'))):
        #景點名稱
        attname.append(soup.select('.property_title a')[j].text)
        attname_url.append(soup.select('.property_title a')[j].get('href'))

        #排名
        rank.append(soup.select('.entry')[j].select('.popRanking')[0].text.strip().split(' ')[1])

        #景點特色
        try:
            spec.append(soup.select('.p13n_reasoning_v2')[j].text.strip().replace('\n',','))
        except:
            spec.append('')

        #景點評分
        try:
            score.append(soup.select('.sprite-ratings')[j].get('alt', ''))
        except:
            score.append('')

        #評論數及連結
        try:
            comment_count.append(soup.select('.more a')[j].text.split('則評論')[0])
            comment_url.append('https://www.tripadvisor.com.tw'+soup.select('.more a')[j].get('href'))
        except:
            comment_count.append('')
            comment_url.append('')

    attractions = pd.DataFrame({'area':area, 'city_1_en':city_1_en, 'city_2_en':city_2_en, \
                                'attname':attname, 'attname_url':attname_url ,'rank':rank, 'spec':spec, 'score':score, \
                                'comment_count':comment_count, 'comment_url':comment_url})
    if not os.path.isfile("attractions.csv"):
        attractions.to_csv("attractions.csv")
    else:
        attractions.to_csv("attractions.csv", mode='a', header=False)

def getnextpage(soup):
    try:
        sighturl = 'https://www.tripadvisor.com.tw'+soup.select('.unified .nav')[1].get('href')
    except:
        sighturl = ''
    return sighturl

def getbasicdata(sighturl):
    re = requests.get(sighturl, headers = headers)
    soup = bs(re.text,'lxml')
    print (soup.select('#taplc_hotels_redesign_header_0 .scopedSearch'))
    #取得洲別,國家,區域,城市1階,城市2階
    choose = soup.select('#taplc_hotels_redesign_header_0 .scopedSearch')[0].text.strip()
    continent = choose.split('›')[0]
    country = choose.split('›')[1]
    area = choose.split('›')[2]
    city_1 = choose.split('›')[3]
    city_2 = choose.split('›')[4]
    city_1_en = sighturl.split('_Prefecture_')[0].split('-Activities-')[-1].split('_')[-1]
    city_2_en = ' '.join(sighturl.split('_Prefecture_')[0].split('-Activities-')[-1].split('_')[:-1])
    print (city_2)
    return continent,country,area,city_1,city_1_en,city_2,city_2_en

if __name__ == '__main__':
    with open('japncitylist.csv', 'r') as japncitylist:
        for citylist in csv.DictReader(japncitylist):
            sighturl = citylist['clist_url']
            city_1_en = sighturl.split('_Prefecture_')[0].split('-Activities-')[-1].split('_')[-1]
            city_2_en = ' '.join(sighturl.split('_Prefecture_')[0].split('-Activities-')[-1].split('_')[:-1])
            try:
                area = sighturl.split('_Prefecture_')[1].split('.')[0]
            except:
                area = ''
            i = 0
            while sighturl != '':
                re = requests.get(sighturl, headers = headers)
                soup = bs(re.text,'lxml')
                getattraction(area, city_1_en, city_2_en, soup)
                sighturl = getnextpage(soup)
                i += 1
                print (i)
                sleep(randint(1,5))

            print ("Finished")
    japncitylist.close()