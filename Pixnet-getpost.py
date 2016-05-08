import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import math
import time
import datetime
import os
import csv

def getblogpost(r,page,blog_url,blog_name,blog_title,category_id,category_name):
    hit_daily,hit_total,comment_count,post_link,public_date,post_title = [],[],[],[],[],[]
    for i in r['articles']:
        hit_daily.append(i['hits']['daily']) #當日瀏覽次數
        hit_total.append(i['hits']['total']) #瀏覽次數
        try:
            comment_count.append(i['info']['comments_count']) #留言數
        except:
            comment_count.append("")
        post_link.append(i['link']) #貼文網址
        public_date.append(datetime.date.fromtimestamp(int(i['public_at'])).strftime('%Y-%m-%d')) #發表時間
        post_title.append(i['title']) #文章標題

    blog_post = pd.DataFrame({'blog_url':blog_url, 'blog_name':blog_name, 'blog_title':blog_title, \
                              'category_id':category_id, 'category_name':category_name, \
                              'hit_daily':hit_daily, 'hit_total':hit_total, 'comment_count':comment_count, \
                               'post_link':post_link, 'public_date':public_date, 'post_title':post_title})
    if not os.path.isfile("blog_post_nocontent.csv"):
        blog_post.to_csv("blog_post_nocontent.csv")
    else:
        blog_post.to_csv("blog_post_nocontent.csv", mode='a', header=False)

if __name__ == '__main__':
    access_token = "3372eba67d7735867c29bfbfc86fc21b"
    with open('categories-29.csv', 'r') as c29:
        t = 1
        for i in csv.DictReader(c29):
            blog_url = i['blog_url']
            blog_name = i['blog_name']
            blog_title = i['blog_title']
            category_id = i['id_child']
            if i['id_child'] == i['id_main']:
                category_name = i['name_main']
            else:
                category_name = i['name_main']+'-'+i['name_child']
            page = 1
            r = requests.get('https://emma.pixnet.cc/blog/articles?user='+ blog_url+'&category_id='+category_id+ \
                             '&page='+str(page)+'&access_token='+access_token).json()
            pages = math.ceil(r['total']/100)
            while page <= pages:
                getblogpost(r,page,blog_url,blog_name,blog_title,category_id,category_name)
                print (t)
                t += 1
                page += 1
                if page <= pages:
                    r = requests.get('https://emma.pixnet.cc/blog/articles?user='+ blog_url+'&category_id='+category_id+ \
                                     '&page='+str(page)+'&access_token='+access_token).json()
                else:
                    break
    c29.close()
    print ("Final Finished")