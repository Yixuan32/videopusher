from flask import Flask, request, render_template, jsonify, g
import os, psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs
import requests, datetime, re
import pandas as pd
import urllib.parse
import boto3
import base64
import os
from clock import scheduled_email
from apscheduler.schedulers.blocking import BlockingScheduler


app = Flask(__name__)


# DATABASE SECTION

def connect_db():
  if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    db = psycopg2.connect(database_url)
  else:
    #database_url = "postgres://dbycbwdngelzjp:6769e3b8027bed07cc33198fb12db69330502f5788d8578284c7fcde25dca1e3@ec2-54-235-133-42.compute-1.amazonaws.com:5432/deeersqn3s60p0"
    database_url = "postgres://nofsstwunlrjut:cb3a80b749c04b4055b5657bfe80e3eedf7e144aaf0ee0a0c6e5d1717d054ced@ec2-174-129-254-220.compute-1.amazonaws.com:5432/d517f20lof6uov"
    db = psycopg2.connect(database_url)
  return db

def get_db():
  if not hasattr(g, 'db'):
    g.db = connect_db()
  return g.db

@app.teardown_appcontext
def teardown_db(error):
  if hasattr(g, 'db'):
    g.db.close()


# WEB APP

@app.route("/")
def index():
  return render_template("main.html")

@app.route('/', methods=['POST'])
def my_form_post():
  text = request.form['user_name']
  processed_text = text.upper()
  return processed_text


# BUTTON Send Now
@app.route('/immediate', methods = ["POST", "GET"])
def immediate():
  if request.method == "POST":
    result = request.form

  # saving user info to variables
  user_info_list = list(result.items())
  
  user_email = str(user_info_list[0][1])
  
  user_topic = str(user_info_list[1][1])
  user_search_params = {'q': user_topic}
  user_url_search_terms = urllib.parse.urlencode(user_search_params)

  
  # SCRAPER
  base = "https://www.youtube.com/results?search_query="
  qstring = user_topic
  r = requests.get(base + qstring)
  page = r.text
  soup = bs(page, 'html.parser')
  vids = soup.findAll('a', attrs={'class': 'yt-uix-tile-link'})
  videolist = []
  for v in vids:
    tmp = 'https://www.youtube.com' + v['href']
    videolist.append(tmp)
  df = pd.DataFrame(videolist)

  ####

  # EMAIL SENDER
  requests.post(
       "https://api.mailgun.net/v3/sandbox1ad7f0d6956b4fcdb728091dbebe3d7b.mailgun.org/messages",
       auth=("api", "33e62e196215815f54660b4d5e261e6f-f7910792-838afa06"),
       data={"from": "Newsletter Delivery Service <postmaster@sandbox1ad7f0d6956b4fcdb728091dbebe3d7b.mailgun.org>",
             "to": "<{}>".format(user_email),
             "subject": "News Briefing on {}".format(user_topic),
             "html": df.to_html()})


  return render_template("immediate.html", result = result)


# BUTTON SUBSCRIBE

@app.route('/result', methods = ["POST", "GET"])
def result():

  if request.method == "POST":
    result = request.form

  # saving user info to variables
  user_info_list = list(result.items())
  user_name = str(user_info_list[0][1])
  user_email = str(user_info_list[1][1])

  #user_email = encrypt(user_email)

  user_topic = str(user_info_list[2][1])
  user_search_params = {'q': user_topic}
  user_url_search_terms = urllib.parse.urlencode(user_search_params)
  
  user_time = str(user_info_list[3][1])

  user_dataframe = pd.DataFrame(columns=['user_name', 'user_email', 'user_topic', 'user_time'])
  user_dataframe1 = pd.DataFrame([[user_name, user_email, user_topic, user_time]], columns=list(user_dataframe.columns))
  user_dataframe = user_dataframe.append(user_dataframe1)

  # saving user info to database
  if os.environ.get('DATABASE_URL'):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = create_engine(DATABASE_URL)
  else:
    DATABASE_URL = "postgres://nofsstwunlrjut:cb3a80b749c04b4055b5657bfe80e3eedf7e144aaf0ee0a0c6e5d1717d054ced@ec2-174-129-254-220.compute-1.amazonaws.com:5432/d517f20lof6uov"
    conn = create_engine(DATABASE_URL)

  user_dataframe.to_sql('user_info', conn, if_exists='append')

  #do the subscribe email sending

  scheduled_email()


  return render_template("result.html", result = result)


#run app

if __name__ == '__main__':
  app.run(debug=True)

