import sys
import time
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape
import sqlite3
import datetime
try:
    import simplejson as json
except ImportError:
    import json
import kindle_mail

conn = sqlite3.connect('items.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS items 
             (id integer, date text, item text, seen boolean)''')
c.execute('''CREATE INDEX IF NOT EXISTS items_id_idx
             ON items (id)''')
conn.commit()


env = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape(['html']))

template = env.get_template("kindle.html")

def load_ids():
    c.execute('''SELECT id FROM items''')
    print(c.fetchall())
    return set()

def make_row(i):
    return [i, datetime.datetime.now(), get_item(i), False]

def isnt_in_db(i):
    c.execute('''SELECT id FROM items WHERE id=?''', (i,))
    return not bool(c.fetchone())

def insert_ids(ids):
    new_ids = filter(isnt_in_db, ids)
    items = list(map(make_row, new_ids))
    print(items)
    c.executemany('''INSERT INTO items VALUES (?,?,?,?)''', items)
    conn.commit()

def get_frontpage_ids(nr_pages=2):
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    r = requests.get(url)
    return r.json()[:nr_pages*30]

def get_item(i):
    url = 'https://hacker-news.firebaseio.com/v0/item/{id}.json'.format(id=i)
    r = requests.get(url)
    return r.text

def build_item_from_row(r):
    return json.loads(r[2])

def build_html(items):
    return template.render(items=items)

def output_items(api_key, to_addr):
    items = list(sorted(map(build_item_from_row, c.execute('''SELECT * FROM items WHERE NOT seen''')), reverse=True, key=lambda x: x["score"]))
    if items:
        kindle_mail.send_email(api_key, to_addr, build_html(items))
        c.execute('''UPDATE items SET seen=1''')
        conn.commit()

def get_todays_update():
    today = datetime.date.today()
    eightpm = datetime.time(20)
    return datetime.datetime.combine(today, eightpm)

UPDATE_DELAY_SECS = 5 * 60

if __name__ == "__main__":
    to_addr = sys.argv[1]
    api_key = sys.argv[2]
    next_update = get_todays_update()
    while True:
        print("Updating items")
        new_ids = get_frontpage_ids()
        insert_ids(new_ids)
        if datetime.datetime.now() > next_update:
            print("Outputting results")
            output_items(api_key, to_addr)
            next_update = next_update + datetime.timedelta(days=1)
        time.sleep(UPDATE_DELAY_SECS)
