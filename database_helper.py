#!/usr/bin/env python3

import sqlite3
import pickle


def init_database():
    init_users_table()
    init_cache()


def init_users_table():
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS rating (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT UNIQUE,
        rate   INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()


def init_cache():
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        url      TEXT,
        response BLOB
    )
    ''')
    conn.commit()
    conn.close()


def update_user_rating(user):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''UPDATE rating SET rate = rate + 1  WHERE name = ?''', (user,))

    if cur.rowcount == 0:  # there is no such user in db
        cur.execute('''INSERT INTO rating (name, rate) VALUES ( ?, ? )''', (user, 1))

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


def get_cached_response(url):
    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''SELECT response FROM cache WHERE url = ?''', (url,))
    row = cur.fetchone()
    result = pickle.loads(row[0]) if row is not None else None

    conn.commit()
    conn.close()

    return result


def remove_response(url):
    init_cache()

    conn = sqlite3.connect('lottery.sqlite')
    cur = conn.cursor()

    cur.execute('''DELETE FROM cache WHERE url = ?''', (url,))
    conn.commit()
    conn.close()
