from flask import Flask, jsonify, request, render_template, session
from functools import wraps
import redis
import psycopg2

app = Flask(__name__)
r = redis.StrictRedis(host="127.0.0.1",port="6379",decode_responses= True ,charset= "utf-8")
con = psycopg2.connect(host="localhost",database="testdb",user="postgres",password="darkmatter")
cur = con.cursor()


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

def authenticated(u,p):
    if r.get(p)==u:
        return True
    return False

def validation(frm,to,msg,inp):
    if len(frm)==0:
        return jsonify({"message": "", "error": "from is missing"})
    elif len(to)==0:
        return jsonify({"message": "", "error": "to is missing"})
    elif len(msg)==0:
        return jsonify({"message": "", "error": "text is missing"})
    if not 6<=len(frm)<=16:
        return jsonify({"message": "", "error": frm+" is invalid"})
    elif not 6<=len(to)<=16:
        return jsonify({"message": "", "error": to+" is invalid"})
    elif not 1<=len(msg)<=120:
        return jsonify({"message": "", "error": msg+" is invalid"})
    if r.exists(frm) and r.exists(to):
        if inp=="inbound":
                return jsonify({"message": "inbound sms ok", "error" : ""})        
        if inp=="outbound":
                if frm==to and r.get(s)==r.get(frm):
                    return jsonify({"message": "", "error" : "sms from "+frm+" to "+to+" blocked by STOP request"})
                if r.exists(frm) and r.exists(to):
                    return jsonify({"message": "outbound sms ok", "error": ""})
    return jsonify({"message": "", "error" : "unknown failure"})

@app.route('/inbound/sms',methods=['POST'])
def receive_sms():
    mt = request.method
    k = list(request.json.keys())
    u = request.authorization.username
    p = request.authorization.password
    # session['user'] = u

    if mt != 'POST':
        return render_template('error.html'),405
    if authenticated(u,p):
        if k==['from','to','text']:
            frm = request.json['from']
            to = request.json['to']
            msg = request.json['text']
            txt = validation(frm,to,msg,"inbound")
            if  not r.get(u)==r.get(to):
                txt = jsonify({"message": "", "error": "to parameter not found"})
            if msg=="STOP" or msg=="STOP\n" or msg=="STOP\r" or msg=="STOP\r\n":
                r.hset("unique_entry",frm,to)
                r.expire(frm,14400)
        else:
            return jsonify({"message": "", "error": "keys are invalid"})
        return txt

    else:
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