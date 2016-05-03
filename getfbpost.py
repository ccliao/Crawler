import requests
import json
import pandas as pd
import os
import datetime
import time

def getdata(r):
    jd = json.loads(r.text)['data']
    df = pd.read_json(json.dumps(jd))

    # 調整時區為台灣時間
    created_time = []
    for i in df['created_time']:
        created_time.append(i.tz_localize('UTC').tz_convert('Asia/Taipei'))

    #貼文按讚數
    reaction_count = []
    for i in df['reactions']:
        reaction_count.append(i['summary']['total_count'])

    #貼文分享數 shares
    share_count = []
    if 'shares' in df:
        for i in df['shares']:
            if i != i: #判讀是否為nan
                share_count.append(0)
            else:
                share_count.append(i['count'])
    else:
        for i in range(len(df['reactions'])):
            share_count.append(0)

    #貼文留言數
    comment_count = []
    if 'comments' in df:
        for i in df['comments']:
            if i != i: #判讀是否為nan
                comment_count.append(0)
            else:
                comment_count.append(i['summary']['total_count'])
    else:
        for i in range(len(df['comments'])):
            comment_count.append(0)

    lion_fb = pd.DataFrame({'created_time': created_time, 'message': df['message'], 'reaction_count': reaction_count, \
                            'share_count': share_count, 'comment_count': comment_count, 'linkname': df['name'], \
                            'link': df['link'], 'postlink': df['permalink_url']})
    if not os.path.isfile("lion_fb.csv"):
        lion_fb.to_csv("lion_fb.csv")
    else:
        lion_fb.to_csv("lion_fb.csv", mode='a', header=False)

def getnextpaging(r):
    paging = json.loads(r.text)['paging']
    if 'next' in paging:
        url = paging['next']
    else:
        url = ''
    return url

def getdaterange():
    print('Input Date(EX.2016/1/1) range, Blank means ALL')
    since = str(input('start date：'))
    until = str(input(' end date：'))
    try:
        if since == '':
            pass
        else:
            datetime.datetime.strptime(since, '%Y/%m/%d')
        if until == '':
            pass
        else:
            until = datetime.datetime.strptime(until, '%Y/%m/%d') + datetime.timedelta(days=1)
            until = time.mktime(datetime.datetime.timetuple(until))
    except:
        print ('something wrong, type again.')
        getdaterange()
    return (since, until)

if __name__ == '__main__':
    ACCESSTOKEN = input('your facebook access token： ')
    fbname = input('your facebook name or id： ')
    since, until = getdaterange()
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=name%2Cmessage%2Ccreated_time%2Cid%2Cshares%2C \
                    reactions.summary(1)%2Clink%2Cpermalink_url%2Ccomments.summary(1) \
                    &limit=100&since={}&until={}&access_token={}'.format(fbname, since, until, ACCESSTOKEN)

    i = 0
    while url != '':
        r = requests.get(url)
        if len(json.loads(r.text)['data']) == 0:
            url = ''
        else:
            getdata(r)
            url = getnextpaging(r)
            i += 1
            print (i)

    print ("Finished")