from flask import Flask, jsonify, request, render_template, session
from datetime import datetime
import redis
import psycopg2
import os


app = Flask(__name__)
r = redis.StrictRedis(host="127.0.0.1",port="6379",decode_responses= True ,charset= "utf-8")
con = psycopg2.connect(host="localhost",database="testdb",user="postgres",password="darkmatter")
cur = con.cursor()
cur.execute('select * from account')
accounts = cur.fetchall()


# Using hashsets because accounts can be different but not usernames, phone numbers
for a in accounts:
	person = {"id":a[0],"auth_id":a[1],"username":a[2]}
	r.hmset(a[2]+":", person)

cur.execute('select number,account_id from phone_number')
phones = cur.fetchall()

for a in phones:
	phone = {"number":a[0],"account_id":a[1]}
	r.hmset(a[0]+":", phone)