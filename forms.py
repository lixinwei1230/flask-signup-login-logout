from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AddressForm(FlaskForm):
  address = StringField('Address', validators=[DataRequired("Please enter an address.")])
  submit = SubmitField("Search")