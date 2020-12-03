## sms-server
A micro service API server that exposes the following 2 APIs that accept JSON data as
input to POST requests.

### Requirements

* [Postman](https://www.getpostman.com/downloads/)
* [Python 3](https://www.python.org/downloads/)
* [Postgres](https://www.postgresql.org)
* [PgAdmin](https://www.pgadmin.org/download/)
* [Redis](https://https://redis.io/download/)

### How to Run this in a local machine

* After installing all requirements above, create a new database in pgadmin called `testdb`
* Now, restore the `schema.sql` dump using `testdb-# \i schema.sql` command in postgres SQL shell
* Run `pip install -r requirements.txt` inside command prompt/terminal from the project folder
* Now run `python main.py`
* Open Postman and keeping method as POST, paste `https://localhost:5000/inbound/sms` for inbound request.
* In 'Authorization tab' enter username and auth_id(password)
* In 'Body' tab, select 'raw' and keep type as JSON type
* Hit send and check the response from below
* Change url to `https://localhost:5000/outbound/sms` to check outbound sms requests
