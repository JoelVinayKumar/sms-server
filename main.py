from depends import *

# Basic Authentication for the user
def authenticated(u,p):
    if r.exists(u+":"):
        s = r.hgetall(u+":")
        if s['auth_id'] == p:
            return True
    return False

def validation(frm,to,msg):
    # If length is 0, it is missing
    if len(frm)==0:
        return jsonify({"message": "", "error": "from is missing"}) 
    elif len(to)==0:
        return jsonify({"message": "", "error": "to is missing"})
    elif len(msg)==0:
        return jsonify({"message": "", "error": "text is missing"})

    # Check for length is in given range
    elif not 6<=len(frm)<=16:
        return jsonify({"message": "", "error": frm+" is invalid"})
    elif not 6<=len(to)<=16:
        return jsonify({"message": "", "error": to+" is invalid"})
    elif not 1<=len(msg)<=120:
        return jsonify({"message": "", "error": msg+" is invalid"})
    else:
        return jsonify({"message": "", "error" : "unknown failure"})

@app.route('/inbound/sms',methods=['POST'])
def receive_sms():
    mt = request.method                 # Receives the http method
    k = list(request.json.keys())       # Lists all JSON keys from request
    u = request.authorization.username  # Username from Basic Authentication
    p = request.authorization.password  # Auth ID from Basic Authentication

    if mt != 'POST':
        return render_template('error.html',status=405),405
    if authenticated(u,p):

        # Check keys from JSON for our requirement
        if k==['from','to','text']:
            frm = request.json['from']
            to = request.json['to']
            msg = request.json['text']
            txt = validation(frm,to,msg)

            # Check if to number belongs to authorized account
            if r.exists(frm+":") and r.exists(to+":"):
                a = r.hgetall(u+":")
                b = r.hgetall(to+":")
                if  not a['id']==b['account_id']:
                    return jsonify({"message": "", "error": "to parameter not found"})

            # If message is STOP, store the numbers for 4 hours
            if msg=="STOP" or msg=="STOP\n" or msg=="STOP\r" or msg=="STOP\r\n":
                record = frm+","+to
                r.set(record,to)
                r.expire(record,50)
            print(r.exists(record))
            if r.exists(frm) and r.exists(to):
                return jsonify({"message": "inbound sms ok", "error" : ""})
        else:
            return jsonify({"message": "", "error": "keys are invalid"})
        return txt

    else:
        # Return http 403 error if authentication is failed
        return render_template('error.html',status=403),403

@app.route('/outbound/sms',methods=['POST'])
def send_sms():
    mt = request.method
    k = list(request.json.keys())
    u = request.authorization.username
    p = request.authorization.password

    if mt != 'POST':
        return render_template('error.html',status=405),405
    
    if authenticated(u,p):
        if k==['from','to','text']:
            frm = request.json['from']
            to = request.json['to']
            msg = request.json['text']
            
            # Check if from,to pair already exists in cache
            record = frm+","+to
            if r.exists(record):
                return jsonify({"message": "", "error" : "sms from "+frm+" to "+to+" blocked by STOP request"})

            # Check if from number belongs to authorized account
            if r.exists(frm+":") and r.exists(to+":"):
                a = r.hgetall(u+":")
                b = r.hgetall(frm+":")
                if  not a['id']==b['account_id']:
                    return jsonify({"message": "", "error": "to parameter not found"})

            #Check for api requests count
            api = {"requests_count":0,"cTime":0,"uTime":0}
            r.hmset(frm+"#",api )


            txt = validation(frm,to,msg)
            if r.exists(frm) and r.exists(to):
                return jsonify({"message": "outbound sms ok", "error": ""})

        else:
            return jsonify({"message": "", "error": "keys are invalid"})
        return txt

    else:
        return render_template('error.html',status=403),403


if __name__ == '__main__':
    app.run(debug=True)
    con.close()