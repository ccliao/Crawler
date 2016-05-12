import requests
import json
import pandas as pd
import os
import datetime
import time

def getdata(r):
    jd = json.loads(r.text)['data']
    df = pd.read_json(json.dumps(jd))

    # 貼文內容
    pmessage, pname, link, permalink_url = [], [], [], []
    if 'message' in df:
        for i in df['message']:
            pmessage.append(i)
    else:
        pmessage=""
    for i in df['name']:
        pname.append(i)
    for i in df['link']:
        link.append(i)
    for i in df['permalink_url']:
        permalink_url.append(i)

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

    # 貼文insights
    Post_Total_Reach, Post_Consumptions, Post_Consumptions_other, Post_Consumptions_photo, Post_Consumptions_link = [], [], [], [], []
    if 'insights' in df:
        for i in df['insights']:
            # 已觸及人數Lifetime Post Total Reach
            if i['data'][4]['title'] == 'Lifetime Post Total Reach':
                Post_Total_Reach.append(i['data'][4]['values'][0]['value'])
            else:
                Post_Total_Reach.append(0)

            # 貼文點擊次數Lifetime Post Consumptions
            if i['data'][44]['title'] == 'Lifetime Post Consumptions':
                Post_Consumptions.append(i['data'][44]['values'][0]['value'])
            else:
                Post_Consumptions.append(0)

            # 貼文點擊次數分類Lifetime Post Consumptions by type
            if i['data'][46]['title'] == 'Lifetime Post Consumptions by type':
                try:
                    Post_Consumptions_other.append(i['data'][46]['values'][0]['value']['other clicks'])
                except:
                    Post_Consumptions_other.append(0)
                try:
                    Post_Consumptions_photo.append(i['data'][46]['values'][0]['value']['photo view'])
                except:
                    Post_Consumptions_photo.append(0)
                try:
                    Post_Consumptions_link.append(i['data'][46]['values'][0]['value']['link clicks'])
                except:
                    Post_Consumptions_link.append(0)
            else:
                Post_Consumptions_other.append(0)
                Post_Consumptions_photo.append(0)
                Post_Consumptions_link.append(0)
    else:
        Post_Total_Reach=0
        Post_Consumptions=0
        Post_Consumptions_other=0
        Post_Consumptions_photo=0
        Post_Consumptions_link=0

    lion_fb = pd.DataFrame(
        {'postdate': created_time, 'message': pmessage, 'reaction_count': reaction_count, 'share_count': share_count, \
         'comment': comment_count, 'linkname': pname, 'link': link, 'postlink': permalink_url, 'type':df['type'], \
         'Post_Total_Reach': Post_Total_Reach, 'Post_Consumptions': Post_Consumptions, \
         'Post_Consumptions_other': Post_Consumptions_other, 'Post_Consumptions_photo': Post_Consumptions_photo, \
         'Post_Consumptions_link': Post_Consumptions_link})

    savefilename = fbname + "_fb-v" + datetime.datetime.now().strftime('%Y%m%d') + ".csv"
    if not os.path.isfile(savefilename):
        lion_fb.to_csv(savefilename)
    else:
        lion_fb.to_csv(savefilename, mode='a', header=False)

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
            since = datetime.datetime.strptime(since, '%Y/%m/%d')
            since = int(time.mktime(datetime.datetime.timetuple(since)))
            # since = int((since - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1))

        if until == '':
            pass
        else:
            until = datetime.datetime.strptime(until, '%Y/%m/%d') + datetime.timedelta(seconds=86399)
            until = int(time.mktime(datetime.datetime.timetuple(until)))
            # until = int((until - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1))
    except:
        print ('something wrong, type again.')
        getdaterange()
    return (since, until)

def getreactionslist(fbname, since, until, ACCESSTOKEN):
    #取得reactions名單
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=id%2Creactions.limit(100) \
            &limit=100&since={}&until={}&access_token={}'.format(fbname, since, until, ACCESSTOKEN)
    while url != '':
        d = requests.get(url).json()
        for i in d['data']:
            if 'reactions' in i:
                r = i['reactions']
                while 1:
                    post_id, user_id, user_name, reaction_type = [], [], [], []
                    if r['data'] == []:
                        break
                    else:
                        for j in r['data']:
                            post_id.append(i['id'])
                            user_id.append(j['id'])
                            user_name.append(j['name'])
                            reaction_type.append(j['type'])
                        reaction_list = pd.DataFrame({'post_id':post_id, 'user_id':user_id, 'user_name':user_name, 'reaction_type':reaction_type})
                        savefilename = fbname+"_FB-reactionlist-v"+datetime.datetime.now().strftime('%Y%m%d')+".csv"
                        if not os.path.isfile(savefilename):
                            reaction_list.to_csv(savefilename)
                        else:
                            reaction_list.to_csv(savefilename, mode='a', header=False)
                        if 'next' not in r['paging']:
                            break
                        else:
                            nexturl = r['paging']['next']
                            r = requests.get(nexturl).json()
        if 'paging' in d:
            if 'next' in d['paging']:
                url = d['paging']['next']
            else:
                url = ''
        else:
            url = ''
    print('Get Reactions List Finished')

def getcommentslist(fbname, since, until, ACCESSTOKEN):
    # 取得comments名單
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=id%2Ccomments.limit(100) \
            &limit=100&since={}&until={}&access_token={}'.format(fbname, since, until, ACCESSTOKEN)
    while url != '':
        d = requests.get(url).json()
        for i in d['data']:
            if 'comments' in i:
                r = i['comments']
                while 1:
                    post_id, user_id, user_name, reaction_type = [], [], [], []
                    for j in r['data']:
                        post_id.append(i['id'])
                        user_id.append(j['from']['id'])
                        user_name.append(j['from']['name'])
                        reaction_type.append('comment')
                    reaction_list = pd.DataFrame(
                        {'post_id': post_id, 'user_id': user_id, 'user_name': user_name, 'reaction_type': reaction_type})
                    savefilename = fbname + "_FB-reactionlist-v" + datetime.datetime.now().strftime('%Y%m%d') + ".csv"
                    if not os.path.isfile(savefilename):
                        reaction_list.to_csv(savefilename)
                    else:
                        reaction_list.to_csv(savefilename, mode='a', header=False)
                    if 'next' not in r['paging']:
                        break
                    else:
                        nexturl = r['paging']['next']
                        r = requests.get(nexturl).json()
        if 'paging' in d:
            if 'next' in d['paging']:
                url = d['paging']['next']
            else:
                url = ''
        else:
            url = ''
    print('Get Comments List Finished')

if __name__ == '__main__':
    ACCESSTOKEN = input('your facebook access token： ')
    fbname = input('your facebook name or id： ')
    since, until = getdaterange()
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=name%2Cmessage%2Ccreated_time%2Cid%2Cshares%2C \
                    reactions.summary(1)%2Clink%2Cpermalink_url%2Ccomments.summary(1)%2Cinsights%2Ctype \
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
    print("Get Post Finished")

    Go = input('Continue to get Reactions&Comments User List(Y/N)： ')
    if (Go == "Y") or (Go == "y"):
        print ("Please wait to get Reactions List")
        getreactionslist(fbname, since, until, ACCESSTOKEN)
        print("Please wait for get Comments List")
        getcommentslist(fbname, since, until, ACCESSTOKEN)
        print("Totally Finished")
    else:
        print ("Totally Finished")

