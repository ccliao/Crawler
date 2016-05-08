import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import math
import time
import datetime
import os
import csv

def getblogtop():
    #旅遊部落客排行榜
    blog_url,blog_name,blog_title = [],[],[]
    rank = 0
    for i in range(7):
        page = i + 1
        r = requests.get('https://www.pixnet.net/blog/bloggers/category/16/{}'.format(page))
        r.encoding = 'utf8'
        soup = bs(r.text, 'lxml')
        for j in range(len(soup.select('#content .author'))):
            blog_url.append(soup.select('.author')[j]['href'].split('/')[-1])
            blog_name.append(soup.select('.author')[j].text)
            blog_title.append(soup.select('.blog-title')[j].text)
            rank += 1
            if rank >= 100:
                break
    travel_blog_top100 = pd.DataFrame({'blog_url':blog_url,'blog_name':blog_name,'blog_title':blog_title})
    travel_blog_top100.to_csv("travel_blog_top100.csv")

def getcategories(rank,blog_url,blog_name,blog_title):
    name_main,id_main,name_child,id_child,site_category_id = [],[],[],[],[]
    access_token = "6f62907291489ecbc220637d4becb51c"
    r = requests.get('https://emma.pixnet.cc/blog/categories?user='+ blog_url+'&access_token='+access_token).json()
    for i in r['categories']:
        if 'child_categories' in i:
            for j in i['child_categories']:
                name_main.append(i['name'])
                id_main.append(i['id'])
                name_child.append(j['name'])
                id_child.append(j['id'])
                if 'site_category_id' in j:
                    site_category_id.append(j['site_category_id'])
                else:
                    site_category_id.append("")
        else:
            name_main.append(i['name'])
            id_main.append(i['id'])
            name_child.append(i['name'])
            id_child.append(i['id'])
            if 'site_category_id' in i:
                site_category_id.append(i['site_category_id'])
            else:
                site_category_id.append("")
    categories = pd.DataFrame({'blog_name':blog_name, 'blog_title':blog_title, 'blog_url':blog_url, \
                               'name_main':name_main, 'id_main':id_main, \
                               'name_child':name_child, 'id_child':id_child, \
                               'site_category_id':site_category_id})
    if not os.path.isfile("categories.csv"):
        categories.to_csv("categories.csv")
    else:
        categories.to_csv("categories.csv", mode='a', header=False)
    print (str(rank)+'.'+blog_url+' Finished')

if __name__ == '__main__':
    if not os.path.isfile("travel_blog_top100.csv"):
        getblogtop()
    with open('travel_blog_top100.csv', 'r') as travel_blog_top100:
        rank = 0
        for i in csv.DictReader(travel_blog_top100):
            rank += 1
            blog_url = i['blog_url']
            blog_name = i['blog_name']
            blog_title = i['blog_title']
            getcategories(rank,blog_url,blog_name,blog_title)