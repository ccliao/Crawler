import requests
import json
import pandas as pd
import os
import datetime
import time
import re
# from dateutil import tz

def getdata(r, gtoken, btoken):
    jd = json.loads(r.text)['data']
    df = pd.read_json(json.dumps(jd))

    # 貼文內容
    pmessage, hashtag, pname, link, permalink_url = [], [], [], [], []
    short_url, original_url, click_count, referrer, platform, country, browser = [],[],[],[],[],[],[]
    short_url2, original_url2, click_count2, referrer2, country2, platform2, browser2 = [],[],[],[],[],[],[]
    if 'message' in df:
        for index,i in enumerate(df['message']):
            # print (index)
            pmessage.append(i)
            if i != i:
                hashtag.append('')
                shorturls = []
                shorturls2 = []
            else:
                hashtag.append(' '.join(j for j in re.findall("#\w+",i)))
                # \S改為\w,因為短網址後面接"。"會產生錯誤
                shorturls = re.findall("http[s]*://(?:goo.gl|bit.ly)/\w+", i)
                shorturls2 = re.findall("http[s]*://(?:goo.gl|bit.ly)/\w+", df['link'][index])
            if shorturls+shorturls2 == []:
                shorturls = {}
            else:
                shorturls = set(shorturls + shorturls2)
            n = 0
            if shorturls != {}:
                s = len(shorturls)
                for shorturl in shorturls:
                    n += 1
                    if n == 1:
                        if 'goo.gl' in shorturl:
                            s_url, o_url, c_count, refer, ct, pf, bs = getgoogleshorturl(shorturl, gtoken)
                            short_url.append(' , '.join(j for j in s_url))
                            original_url.append(' , '.join(j for j in o_url))
                            click_count.append(' , '.join(str(j) for j in c_count))
                            referrer.append(' , '.join(j for j in refer))
                            country.append(' , '.join(j for j in ct))
                            platform.append(' , '.join(j for j in pf))
                            browser.append(' , '.join(j for j in bs))
                            if s == 1:
                                short_url2.append('')
                                original_url2.append('')
                                click_count2.append('')
                                referrer2.append('')
                                country2.append('')
                                platform2.append('')
                                browser2.append('')
                        elif 'bit.ly' in shorturl:
                            s_url, o_url, c_count, refer, ct, pf, bs = getbitlyshorturl(shorturl, btoken)
                            short_url.append(' , '.join(j for j in s_url))
                            original_url.append(' , '.join(j for j in o_url))
                            click_count.append(' , '.join(str(j) for j in c_count))
                            referrer.append(' , '.join(j for j in refer))
                            country.append(' , '.join(j for j in ct))
                            platform.append(' , '.join(j for j in pf))
                            browser.append(' , '.join(j for j in bs))
                            if s == 1:
                                short_url2.append('')
                                original_url2.append('')
                                click_count2.append('')
                                referrer2.append('')
                                country2.append('')
                                platform2.append('')
                                browser2.append('')
                        else:
                            short_url.append('')
                            original_url.append('')
                            click_count.append('')
                            referrer.append('')
                            country.append('')
                            platform.append('')
                            browser.append('')
                    elif n == 2:
                        if 'goo.gl' in shorturl:
                            s_url, o_url, c_count, refer, ct, pf, bs = getgoogleshorturl(shorturl, gtoken)
                            short_url2.append(' , '.join(j for j in s_url))
                            original_url2.append(' , '.join(j for j in o_url))
                            click_count2.append(' , '.join(str(j) for j in c_count))
                            referrer2.append(' , '.join(j for j in refer))
                            country2.append(' , '.join(j for j in ct))
                            platform2.append(' , '.join(j for j in pf))
                            browser2.append(' , '.join(j for j in bs))
                        elif 'bit.ly' in shorturl:
                            s_url, o_url, c_count, refer, ct, pf, bs = getbitlyshorturl(shorturl, btoken)
                            short_url2.append(' , '.join(j for j in s_url))
                            original_url2.append(' , '.join(j for j in o_url))
                            click_count2.append(' , '.join(str(j) for j in c_count))
                            referrer2.append(' , '.join(j for j in refer))
                            country2.append(' , '.join(j for j in ct))
                            platform2.append(' , '.join(j for j in pf))
                            browser2.append(' , '.join(j for j in bs))
                        else:
                            short_url2.append('')
                            original_url2.append('')
                            click_count2.append('')
                            referrer2.append('')
                            country2.append('')
                            platform2.append('')
                            browser2.append('')
                    else:
                        print (str(n)+'-have more shorturl!!!')
            else:
                short_url.append('')
                original_url.append('')
                click_count.append('')
                referrer.append('')
                country.append('')
                platform.append('')
                browser.append('')
                short_url2.append('')
                original_url2.append('')
                click_count2.append('')
                referrer2.append('')
                country2.append('')
                platform2.append('')
                browser2.append('')
    else:
        pmessage.append('')
        hashtag.append('')
        short_url.append('')
        original_url.append('')
        click_count.append('')
        referrer.append('')
        country.append('')
        platform.append('')
        browser.append('')
        short_url2.append('')
        original_url2.append('')
        click_count2.append('')
        referrer2.append('')
        country2.append('')
        platform2.append('')
        browser2.append('')
    # print ('message完成')

    for i in df['name']:
        pname.append(i)
    for i in df['link']:
        link.append(i)
    for i in df['permalink_url']:
        permalink_url.append(i)
    # print ('name,link,permalink_url完成')

    # 調整時區為台灣時間
    created_time = []
    for i in df['created_time']:
        created_time.append(i.tz_localize('UTC').tz_convert('Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S %A'))
    # print ('created_time完成')

    #貼文按讚數
    reaction_count = []
    for i in df['reactions']:
        if i != i:
            reaction_count.append(0)
        else:
            reaction_count.append(i['summary']['total_count'])
    # print('reaction_count完成')

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
    # print('share_count完成')

    #貼文留言數
    comment_count = []
    if 'comments' in df:
        for i in df['comments']:
            if i != i: #判讀是否為nan
                comment_count.append(0)
            else:
                if 'total_count' in i['summary']:
                    comment_count.append(i['summary']['total_count'])
                else:
                    comment_count.append(0)
    else:
        for i in range(len(df['comments'])):
            comment_count.append(0)
    # print('comment_count完成')

    # 貼文insights
    Post_Total_Reach, Post_Consumptions, Post_Consumptions_other, Post_Consumptions_photo, Post_Consumptions_link = [], [], [], [], []
    if 'insights' in df:
        for i in df['insights']:
            # 已觸及人數Lifetime Post Total Reach
            if i['data'][4]['title'] == 'Lifetime Post Total Reach':
                Post_Total_Reach.append(i['data'][4]['values'][0]['value'])
            else:
                Post_Total_Reach.append('')

            # 貼文點擊次數Lifetime Post Consumptions
            if i['data'][44]['title'] == 'Lifetime Post Consumptions':
                Post_Consumptions.append(i['data'][44]['values'][0]['value'])
            else:
                Post_Consumptions.append('')

            # 貼文點擊次數分類Lifetime Post Consumptions by type
            if i['data'][46]['title'] == 'Lifetime Post Consumptions by type':
                try:
                    Post_Consumptions_other.append(i['data'][46]['values'][0]['value']['other clicks'])
                except:
                    Post_Consumptions_other.append('')
                try:
                    Post_Consumptions_photo.append(i['data'][46]['values'][0]['value']['photo view'])
                except:
                    Post_Consumptions_photo.append('')
                try:
                    Post_Consumptions_link.append(i['data'][46]['values'][0]['value']['link clicks'])
                except:
                    Post_Consumptions_link.append('')
            else:
                Post_Consumptions_other.append('')
                Post_Consumptions_photo.append('')
                Post_Consumptions_link.append('')
    else:
        Post_Total_Reach=''
        Post_Consumptions=''
        Post_Consumptions_other=''
        Post_Consumptions_photo=''
        Post_Consumptions_link=''
    # print('insights完成')

    lion_fb = pd.DataFrame(
        {'postdate': created_time, 'message': pmessage, 'reaction_count': reaction_count, 'share_count': share_count, \
         'comment_count': comment_count, 'linkname': pname, 'link': link, 'postlink': permalink_url, 'type':df['type'], \
         'Post_Total_Reach': Post_Total_Reach, 'Post_Consumptions': Post_Consumptions, \
         'Post_Consumptions_other': Post_Consumptions_other, 'Post_Consumptions_photo': Post_Consumptions_photo, \
         'Post_Consumptions_link': Post_Consumptions_link, 'shorturl':short_url, 'originalurl':original_url, \
         'clickcount':click_count, 'referrer':referrer, 'platform':platform, 'country':country, 'browser':browser, \
         'shorturl2':short_url2, 'originalurl2':original_url2, 'clickcount2':click_count2, 'referrer2':referrer2, \
         'platform2':platform2, 'country2':country2, 'browser2':browser2, 'hashtag':hashtag},
        columns = ["postdate","postlink","type","message","hashtag","link","linkname","reaction_count","share_count","comment_count", \
                   "Post_Total_Reach","Post_Consumptions","Post_Consumptions_link","Post_Consumptions_photo", \
                   "Post_Consumptions_other","shorturl","originalurl","clickcount","referrer","country","browser","platform",\
                   "shorturl2","originalurl2","clickcount2","referrer2","country2","browser2","platform2"])

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

def getgoogleshorturl(glink, gtoken):
    short_url, original_url, click_count, referrer, country, platform, browser = [], [], [], [], [], [], []
    if gtoken == '':
        short_url.append('')
        original_url.append('')
        click_count.append('')
        referrer.append('')
        country.append('')
        platform.append('')
        browser.append('')
    else:
        time.sleep(1)
        gurl = 'https://www.googleapis.com/urlshortener/v1/url?shortUrl={}&projection=FULL&key={}'.format(glink, gtoken)
        req= requests.get(gurl).json()

        #僅先納入alltime,尚有month,week,day,twoHours
        short_url.append(glink) #短網址
        original_url.append(req['longUrl']) #原網址
    #     d = datetime.datetime.strptime(req['created'][0:19], "%Y-%m-%dT%H:%M:%S")
    #     d = d.replace(tzinfo=tz.gettz('UTC'))
    #     shorturlcreatedtime.append(str(d.astimezone(tz.gettz('Asia/Taipei')).date()))  #短址設立日期
        click_count.append(req['analytics']['allTime']['shortUrlClicks']) #短址點擊量
        for i in req['analytics']['allTime']['referrers']:
            referrer.append(str(i['count'])+' from '+i['id']) #短址點擊量來源
        for i in req['analytics']['allTime']['platforms']:
            platform.append(str(i['count'])+' from '+i['id']) #短址點擊量平台
        for i in req['analytics']['allTime']['countries']:
            country.append(str(i['count'])+' from '+i['id']) #短址點擊量國家
        for i in req['analytics']['allTime']['browsers']:
            browser.append(str(i['count'])+' from '+i['id']) #短址點擊量國家
    return short_url, original_url, click_count, referrer, country, platform, browser

def getbitlyshorturl(blink, btoken):
    short_url, original_url, click_count, referrer, country, platform, browser = [], [], [], [], [], [], []
    if btoken == '':
        short_url.append('')
        original_url.append('')
        click_count.append('')
        referrer.append('')
        country.append('')
        platform.append('')
        browser.append('')
    else:
        #透過bit.ly取得短網址點擊相關資訊
        burl_ref = 'https://api-ssl.bitly.com/v3/link/referrers?access_token={}&link={}'.format(btoken, blink) #取得點擊來源
        burl_click = 'https://api-ssl.bitly.com/v3/link/clicks?access_token={}&link={}'.format(btoken, blink) #取得點擊數
        burl_country = 'https://api-ssl.bitly.com/v3/link/countries?access_token={}&link={}'.format(btoken, blink) #取得點擊國家
        burl_long = 'https://api-ssl.bitly.com/v3/expand?access_token={}&shortUrl={}'.format(btoken, blink) #取得原網址
        #與goo.gl相比,無platform與browser來源判讀

        time.sleep(1)
        r_ref = requests.get(burl_ref).json()
        time.sleep(1)
        r_click = requests.get(burl_click).json()
        time.sleep(1)
        r_country = requests.get(burl_country).json()
        time.sleep(1)
        r_long = requests.get(burl_long).json()

        short_url.append(blink) #短網址
        original_url.append(r_long['data']['expand'][0]['long_url']) #原網址
        click_count.append(r_click['data']['link_clicks']) #點擊數
        for ref in r_ref['data']['referrers']:
            referrer.append(str(ref['clicks'])+'-'+ref['referrer']) #點擊來源
        for ref in r_country['data']['countries']:
            country.append(str(ref['clicks'])+'-'+ref['country']) #點擊來源
        platform.append('') #bitly無資料但google有
        browser.append('') #bitly無資料但google有
    return short_url, original_url, click_count, referrer, country, platform, browser

if __name__ == '__main__':
    ACCESSTOKEN = input('your facebook access token： ')
    fbname = input('your facebook name or id： ')
    gtoken = input('your goo.gl api key： ')
    btoken = input('your bit.ly api key： ')
    since, until = getdaterange()
    url = 'https://graph.facebook.com/v2.6/{}/posts?fields=name%2Cmessage%2Ccreated_time%2Cid%2Cshares%2C \
                    reactions.summary(1)%2Clink%2Cpermalink_url%2Ccomments.summary(1)%2Cinsights%2Ctype \
                    &since={}&until={}&access_token={}'.format(fbname, since, until, ACCESSTOKEN)
#&limit=100
    page = 1
    while url != '':
        r = requests.get(url)
        if len(json.loads(r.text)['data']) == 0:
            url = ''
        else:
            # print("第" + str(page) + "頁開始")
            getdata(r,gtoken,btoken)
            # print("第" + str(page) + "頁結束")
            print (page)
            url = getnextpaging(r)
            page += 1
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
