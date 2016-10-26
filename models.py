from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

import geocoder
import urllib2
import json


db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True)
  username = db.Column(db.String(100))
  pwdhash = db.Column(db.String(100))

  def __init__(self, email, username, password):
    self.username = username.title()
    self.email = email.lower()
    self.set_password(password)
     
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)

class Minions(db.Model):
  __tablename__ = 'minions'
  email = db.Column(db.String(100), primary_key=True)
  happiness = db.Column(db.Integer)
  hungry = db.Column(db.Integer)

  def __init__(self, email, happiness, hungry):
    self.email = email.lower()
    self.happiness = happiness
    self.hungry = hungry

  def get_happiness(self):
    return self.happiness

  def get_hungry(self):
    return self.hungry

# p = Place()
# places = p.query("1600 Amphitheater Parkway Mountain View CA")
class Place(object):
  def meters_to_walking_time(self, meters):
    # 80 meters is one minute walking time
    return int(meters / 80)  

  def wiki_path(self, slug):
    return urllib2.urlparse.urljoin("http://en.wikipedia.org/wiki/", slug.replace(' ', '_'))
  
  def address_to_latlng(self, address):
    g = geocoder.google(address)
    return (g.lat, g.lng)

  def query(self, address):
    lat, lng = self.address_to_latlng(address)
    key = 'AIzaSyAMy9cOSxb61112OjzIyr0OfItQB0DD9Ck'
    
    query_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={0},{1}&radius=1000&type=cafe&key={2}'.format(lat, lng, key)
    g = urllib2.urlopen(query_url)
    results = g.read()
    g.close()

    data = json.loads(results)
    
    places = []
    for place in data['results']:
      name = place['name']
      address = place['vicinity']
      lat = place['geometry']['location']['lat']
      lng = place['geometry']['location']['lng']

      d = {
        'name': name,
        'url': 'https://www.yelp.com/search?find_desc=' + name + '&find_loc=' + address,
        'address': address,
        'lat': lat,
        'lng': lng
      }

      places.append(d)

    return places

