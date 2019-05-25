# sms-server
A micro service API server that exposes the following 2 APIs that accept JSON data as
input to POST requests.

## How to Run this in a local machine

* Download and run `pip install -r requirements.txt` inside command prompt/terminal
* Now run `python main.py`
* Open Postman and keeping method as POST, paste `https://localhost:5000/inbound/sms` for inbound request.
* In 'Authorization tab' enter username and auth_id(password)
* In 'Body"' tab, select 'raw' and keep type as JSON type
* Hit send and check the response from below
