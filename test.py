import requests
import json
import psycopg2
from datetime import datetime
import time

print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
conn = psycopg2.connect(database="postgres", user="SuM_", host="127.0.0.1", port="5432")
print("opened database successfully")
cur = conn.cursor()
# cur.execute("CREATE TABLE Cars(Id INTEGER PRIMARY KEY, Name VARCHAR(20), Price INT)")
# cur.execute("INSERT INTO syp VALUES(1,'Audi',10, '2004-10-19 10:23:54')")
# cur.execute("INSERT INTO syp VALUES(2,'Mercedes', 20, '2004-10-19 10:23:54')")
# cur.execute("INSERT INTO syp VALUES(3,'Skoda',30, '2004-10-19 10:23:54')")
# cur.execute("INSERT INTO syp VALUES(4,'Volvo',40, '2004-10-19 10:23:54')")
# cur.execute("DELETE from syp where user_id='2';")

# headers = {'client_id' :'580fe188a753b93289626cc5', 'public_key': '800260ed5fd41898dfeec0ae89a128', 'secret':'7252ac63e7fd1e2a367384e14248b4', 'username': 'plaid_test', 'password' : 'plaid_good' ,'type':'wells'}
# r = requests.post("https://tartan.plaid.com/connect", data=headers)
# print(r.text.accounts)

headers = {'client_id':'580fe188a753b93289626cc5', 'public_key': '800260ed5fd41898dfeec0ae89a128', 'secret':'7252ac63e7fd1e2a367384e14248b4', 'username':'plaid_test', 'password':'plaid_good' ,'type':'wells'}
response = requests.post("https://tartan.plaid.com/connect", json=headers)
json_data = json.loads(response.text)
print json_data


account = json_data['accounts'][0]['_user']
for i in range(len(json_data['transactions'])):
  location = json_data['transactions'][i]['name']
  transaction= json_data['transactions'][i]
  if 'category_id' not in transaction:
	print 'not in this data'
  else:
    category_id = int(transaction['category_id'])
    if category_id >= 13005000 and category_id <= 13005059:
      print 'hehe'
	
conn.commit()
conn.close()