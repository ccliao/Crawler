import requests
import json
import pandas as pd
import os

def getdata(r):
    jd = json.loads(r.text)['data']
    df = pd.read_json(json.dumps(jd))

    #貼文按讚數
    rcount = []
    for i in df['reactions']:
        rcount.append(i['summary']['total_count'])

    #貼文分享數 shares
    share = []
    if 'shares' in df:
        for i in df['shares']:
            if i != i: #判讀是否為nan
                share.append(0)
            else:
                share.append(i['count'])
    else:
        for i in range(len(df['reactions'])):
            share.append(0)

    #貼文留言數
    comment = []
    if 'comments' in df:
        for i in df['comments']:
            if i != i: #判讀是否為nan
                comment.append(0)
            else:
                comment.append(i['summary']['total_count'])
    else:
        for i in range(len(df['comments'])):
            comment.append(0)

    lion_fb = pd.DataFrame({'postdate':df['created_time'], 'message':df['message'], 'rcount':rcount, 'share':share, 'comment':comment,\
                      'linkname':df['name']  , 'link':df['link'], 'postlink':df['permalink_url']})
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

if __name__ == '__main__':
    ACCESSTOKEN = input('your facebook access token： ')
    fbname = input('your facebook name or id： ')
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=name%2Cmessage%2Ccreated_time%2Cid%2Cshares%2C \
                    reactions.summary(1)%2Clink%2Cpermalink_url%2Ccomments.summary(1) \
                    &limit=100&access_token={}'.format(fbname, ACCESSTOKEN)

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