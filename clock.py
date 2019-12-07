from apscheduler.schedulers.blocking import BlockingScheduler
import requests, os, datetime, re
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.parse
import boto3
import base64
import os


sched = BlockingScheduler(timezone="America/New_York")

if os.environ.get('DATABASE_URL'):
  DATABASE_URL = os.environ.get('DATABASE_URL')
  conn = create_engine(DATABASE_URL)
else:
  DATABASE_URL = "postgres://nofsstwunlrjut:cb3a80b749c04b4055b5657bfe80e3eedf7e144aaf0ee0a0c6e5d1717d054ced@ec2-174-129-254-220.compute-1.amazonaws.com:5432/d517f20lof6uov"
  conn = create_engine(DATABASE_URL)
user_time = pd.read_sql("SELECT user_time FROM user_info", conn)
user_time_v = user_time['user_time'].values[0]

@sched.scheduled_job('cron',hour=user_time_v [0:2], minute=user_time_v[3:5])
def scheduled_email():
  # user_time = pd.read_sql("SELECT user_time FROM user_info", conn)
  # user_time_v = user_time['user_time'].values[0]
  userr=pd.read_sql("SELECT * FROM user_info", conn)
  user=[]
  for ii in userr.values:
        if ii[4]==user_time_v:
              user=ii
              break
  #user_email = pd.read_sql("SELECT user_email FROM user_info where user_time= "+ user_time_v, conn)
  #user_topic = pd.read_sql("SELECT user_topic FROM user_info where user_time= "+ user_time_v, conn)

  user_email_v=user[2]
  user_topic_v=user[3]
  # user_search_params = {'q': user_topic_v}
  # user_url_search_terms = urllib.parse.urlencode(user_search_params)

  print(5555555)
  # SCRAPER
  base="https://www.youtube.com/results?search_query="
  qstring =user[3]
  r = requests.get(base + qstring)
  page = r.text
  soup = bs(page, 'html.parser')
  vids = soup.findAll('a', attrs={'class': 'yt-uix-tile-link'})
  videolist = []
  for v in vids:
    tmp = 'https://www.youtube.com' + v['href']
    videolist.append(tmp)
  df = pd.DataFrame(videolist)

  print(5555555)
  # EMAIL SENDER
  requests.post(
    "https://api.mailgun.net/v3/sandbox1ad7f0d6956b4fcdb728091dbebe3d7b.mailgun.org/messages",
    auth=("api", "33e62e196215815f54660b4d5e261e6f-f7910792-838afa06"),
    data={"from": "Video Push Service <mailgun@sandbox1ad7f0d6956b4fcdb728091dbebe3d7b.mailgun.org>",
          "to": "<{}>".format(user_email_v),
          "subject": "Video links on {}".format(user_topic_v),
          "html": df.to_html(),
          })
  print(5555555)
# sched.start()
if __name__ == '__main__':
  scheduled_email()

