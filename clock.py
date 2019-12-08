import requests
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs
import pandas as pd
import os



def scheduled_email():
    if os.environ.get('DATABASE_URL'):
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = create_engine(DATABASE_URL)
    else:
        DATABASE_URL = "postgres://nofsstwunlrjut:cb3a80b749c04b4055b5657bfe80e3eedf7e144aaf0ee0a0c6e5d1717d054ced@ec2-174-129-254-220.compute-1.amazonaws.com:5432/d517f20lof6uov"
        conn = create_engine(DATABASE_URL)

    user_email = pd.read_sql("SELECT user_email FROM user_info", conn)
    user_topic = pd.read_sql("SELECT user_topic FROM user_info", conn)
    user_time = pd.read_sql("SELECT user_time FROM user_info", conn)

    user_email_v = user_email['user_email'].values[-1]
    user_topic_v = user_topic['user_topic'].values[-1]
    user_time_v = user_time['user_time'].values[-1]

    # SCRAPER
    base = "https://www.youtube.com/results?search_query="
    qstring = user_topic_v
    r = requests.get(base + qstring)
    page = r.text
    soup = bs(page, 'html.parser')
    vids = soup.findAll('a', attrs={'class': 'yt-uix-tile-link'})
    videolist = []
    for v in vids:
        tmp = 'https://www.youtube.com' + v['href']
        videolist.append(tmp)
    df = pd.DataFrame(videolist)

    # EMAIL SENDER
    print(user_time_v[0:2])
    print(user_time_v[3:5])
    print(user_email_v)
    print(user_topic_v)

    return user_email_v, user_topic_v, df, user_time_v


