from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Minions, Place
from forms import AddressForm
import logging
import json

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
