#!/usr/bin/env python3

import sqlite3
import pickle


def init_database():
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name            TEXT UNIQUE,
        reviewer_rate   INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS cache (
        id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        url      TEXT,
        response BLOB
    );
    ''')
    conn.commit()
    conn.close()


def update_user_rating(user):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''UPDATE users SET reviewer_rate = reviewer_rate + 1  WHERE name = ?''', (user,))
    print("User's rating updated: ", user)

    if cur.rowcount == 0:  # there is no such user in db
        cur.execute('''INSERT INTO users (name, reviewer_rate) VALUES ( ?, ? )''', (user, 1))
        print ('User added to db: ', user)

    conn.commit()
    conn.close()


def cache_response(url, etag):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    pdata = pickle.dumps(etag, pickle.HIGHEST_PROTOCOL)
    cur.execute('''UPDATE cache SET response = ?  WHERE url = ?''', (sqlite3.Binary(pdata), url))

    if cur.rowcount == 0:  # there is no cached response with that url
        cur.execute('''INSERT INTO cache (url, response) VALUES ( ?, ? )''', (url, sqlite3.Binary(pdata)))

    conn.commit()
    conn.close()


def fetch_cached_response(url):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''SELECT response FROM cache WHERE url = ?''', (url,))
    row = cur.fetchone()
    result = pickle.loads(row[0]) if row is not None else None

    conn.commit()
    conn.close()
    return result


def remove_response(url):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''DELETE FROM cache WHERE url = ?''', (url,))
    conn.commit()
    conn.close()

def get_user_score(user):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''SELECT reviewer_rate FROM users WHERE name = ?''', (user,))
    result = cur.fetchone()

    if result is not None:
        result = result[0]
    else:
        cur.execute('''INSERT INTO users (name, reviewer_rate) VALUES ( ?, ? )''', (user, 0))
        result = 0

    conn.commit()
    conn.close()
    return result


def select_user_with_min_score(users):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''SELECT name, MIN(reviewer_rate) FROM users WHERE name IN ?''', (users,))
    conn.commit()
    conn.close()