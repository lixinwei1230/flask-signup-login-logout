from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Minions, Place
from forms import AddressForm
import logging
import requests
import json
import psycopg2
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/learningflask'
db.init_app(app)

app.secret_key = "development-key"

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():

  if request.method == "POST":

    #if 'email' in session:
      #return '{"movie": "failed!"}'

    logger.info(request.get_json())
    email = request.get_json()['email'].lower()
    password = request.get_json()['password']

    user = User.query.filter_by(email=email).first()
    if user is not None and user.check_password(password):
      session['email'] = email

      minion = Minions.query.filter_by(email=email).first()
      happiness = minion.get_happiness()
      hungry = minion.get_hungry()

      status = {'status': 'ok!', 'happiness': happiness, 'hungry': hungry}
      logger.info('login success!')
      logger.info(status)
      return json.dumps(status)


    else:
      logger.info('login failed!')
      return '{"status": "failed!"}'

@app.route("/status", methods=["GET", "POST"])
def status():

  if request.method == "POST":

    if 'email' in session:
      logger.info(request.get_json())
      status = request.get_json()['loginStatus']
      if status == 'ok':
        newMinion = Minions(session['email'], 100, 0)
        db.session.add(newMinion)
        db.session.commit()
        return '{"status": "ok!"}'

  elif request.method == "GET":

    if 'email' in session:
      minion = Minions.query.filter_by(email=session['email']).first()
      happiness = minion.get_happiness()
      hungry = minion.get_hungry()

      status = {'happiness': happiness, 'hungry': hungry}
      logger.info('login success!')
      logger.info(status)
      return json.dumps(status)

@app.route("/transaction", methods=["GET", "POST"])
def transaction():

  if request.method == "GET":

    logger.info('this is get request')

    #if 'email' in session:
    #loginemail = session['email']
    conn = psycopg2.connect(database="learningflask", user="SuM_", host="127.0.0.1", port="5432")
    print("opened database successfully")
    cur = conn.cursor()

    headers = {'client_id': '580fe188a753b93289626cc5', 'public_key': '800260ed5fd41898dfeec0ae89a128',
               'secret': '7252ac63e7fd1e2a367384e14248b4', 'username': 'plaid_test', 'password': 'plaid_good',
               'type': 'wells'}
    response = requests.post("https://tartan.plaid.com/connect", data=headers)
    json_data = json.loads(response.text);
    account = json_data['accounts'][0]['_user']
    # print(json_data)
    for i in range(len(json_data['transactions'])):
      location = json_data['transactions'][i]['name']
      transaction = json_data['transactions'][i]
      tran_id = json_data['transactions'][i]['_id']
      if 'category_id' not in transaction:
        print 'not in this data'
      else:
        category_id = int(transaction['category_id'])
        if category_id >= 13005000 and category_id <= 13005059:
          # 13005012 Papa Johns Pizza  13005043  Gregorys Coffee  13005043 Krankies Coffee
          try:
            cur.execute('INSERT INTO transaction (transaction_id, email, bank_account, shop_name, amount, checked) VALUES (%s, %s, %s, %s, %s, %s)', (tran_id, 'xinweili@usc.edu', 'plaid_test', transaction['name'], int(transaction['amount']), int(0)))
          except psycopg2.IntegrityError:
            conn.rollback()
          else:
            conn.commit()
    rows = cur.execute("""SELECT shop_name, SUM(amount) FROM transaction WHERE checked=1 GROUP BY shop_name""")
    columns = ('shop_name', 'amount')
    result = []
    for row in cur.fetchall():
      result.append(dict(zip(columns, row)))

    final_json = json.dumps(result, indent=2)

    cur.execute('UPDATE transaction SET checked=1 WHERE checked=0')
    conn.commit()
    conn.close()
    return final_json


@app.route("/logout")
def logout():
  session.pop('email', None)
  return redirect(url_for('index'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
  if request.method == 'POST':
    logger.info(request.get_json())
    email = request.get_json()['email']
    username = request.get_json()['username']
    password = request.get_json()['password']

    newuser = User(email, username, password)
    db.session.add(newuser)
    db.session.commit()

    session['email'] = newuser.email

    logger.info('post success')
    status = '{"status": "ok!"}'
    return status

@app.route("/home", methods=["GET", "POST"])
def home():

  form = AddressForm()

  places = []
  my_coordinates = (34.023076, -118.2870456)

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('home.html', form=form)
    else:
      # get the address
      address = form.address.data 

      # query for places around it
      p = Place()
      my_coordinates = p.address_to_latlng(address)
      places = p.query(address)

      # return those results
      return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

  elif request.method == 'GET':
    return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=9000, debug=False)
