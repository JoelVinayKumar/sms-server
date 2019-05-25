'''
@author Joel Vinay Kumar
@version 1.0
@project SMS server

Import Statements
'''
from flask import Flask, jsonify, request, render_template, session
import redis
import psycopg2

'''
Setting up environment with Flask, Redis and Postgres
'''
app = Flask(__name__)
r = redis.StrictRedis(host="127.0.0.1",port="6379",decode_responses= True ,charset= "utf-8")
con = psycopg2.connect(host="localhost",database="testdb",user="postgres",password="darkmatter")
cur = con.cursor()

'''
Copy all data from testdb in postgres to redis 
'''
cur.execute('select * from account')
accounts = cur.fetchall()
for a in accounts:
    r.set(a[0],a[1])
    r.set(a[1],a[2])
    r.set(a[2],a[0])
cur.execute('select number,account_id from phone_number')
phones = cur.fetchall()
for a in phones:
    r.set(a[0],a[1])
    r.set(a[1],a[0])
cur.close()

# Basic Authentication for the user
def authenticated(u,p):
    if r.get(p)==u:
        return True
    return False

# Minimum validation required for input JSON
def validation(frm,to,msg,inp):
    # If length is 0, it is missing
    if len(frm)==0:
        return jsonify({"message": "", "error": "from is missing"}) 
    elif len(to)==0:
        return jsonify({"message": "", "error": "to is missing"})
    elif len(msg)==0:
        return jsonify({"message": "", "error": "text is missing"})

    # Check for length is in given range
    if not 6<=len(frm)<=16:
        return jsonify({"message": "", "error": frm+" is invalid"})
    elif not 6<=len(to)<=16:
        return jsonify({"message": "", "error": to+" is invalid"})
    elif not 1<=len(msg)<=120:
        return jsonify({"message": "", "error": msg+" is invalid"})
    
    # If both exist, check for method and perform tasks
    if r.exists(frm) and r.exists(to):
        if inp=="inbound":
                return jsonify({"message": "inbound sms ok", "error" : ""})        
        if inp=="outbound":
                if r.get(to)==r.get(frm):
                    return jsonify({"message": "", "error" : "sms from "+frm+" to "+to+" blocked by STOP request"})
                if r.exists(frm) and r.exists(to):
                    return jsonify({"message": "outbound sms ok", "error": ""})
    return jsonify({"message": "", "error" : "unknown failure"})

@app.route('/inbound/sms',methods=['POST'])
def receive_sms():
    mt = request.method                 # Receives the http method
    k = list(request.json.keys())       # Lists all JSON keys from request
    u = request.authorization.username  # Username from Basic Authentication
    p = request.authorization.password  # Auth ID from Basic Authentication

    if mt != 'POST':
        return render_template('error.html'),405
    if authenticated(u,p):

        # Check keys from JSON for our requirement
        if k==['from','to','text']:
            frm = request.json['from']
            to = request.json['to']
            msg = request.json['text']
            txt = validation(frm,to,msg,"inbound")

            # Check if to number belongs to authorized account
            if  not r.get(u)==r.get(to):
                txt = jsonify({"message": "", "error": "to parameter not found"})

            # If message is STOP, store the numbers for 4 hours
            if msg=="STOP" or msg=="STOP\n" or msg=="STOP\r" or msg=="STOP\r\n":
                r.hset("unique_entry",frm,to)
                r.expire(frm,14400)
        else:
            return jsonify({"message": "", "error": "keys are invalid"})
        return txt

    else:
        # Return http 403 error if authentication is failed
        return render_template('error.html'),403

@app.route('/outbound/sms',methods=['POST'])
def send_sms():
    mt = request.method
    k = list(request.json.keys())
    u = request.authorization.username
    p = request.authorization.password

    if mt != 'POST':
        return render_template('error.html'),405
    if authenticated(u,p):
        if k==['from','to','text']:
            frm = request.json['from']
            to = request.json['to']
            msg = request.json['text']
            txt = validation(frm,to,msg,"outbound")

            # Check if from number belongs to authorized account
            if  not r.get(u)==r.get(frm):
                txt = jsonify({"message": "", "error": "to parameter not found"})

        else:
            return jsonify({"message": "", "error": "keys are invalid"})
        return txt

    else:
        return render_template('error.html'),403
if __name__=='__main__':
    app.run('127.0.0.1',5000,debug=True)
    con.close()
