from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, SelectField, SubmitField, Form
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, length, NumberRange
from .models import Produk

class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=3)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=7)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=7)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class MuaForm(FlaskForm):
    nama_mua = StringField('Nama MUA', validators=[DataRequired()])
    lokasi = StringField('Lokasi', validators=[DataRequired()])
    detail_lokasi = StringField('Detail Lokasi', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    add_mua = SubmitField('Tambah')

class ProdukForm(FlaskForm):
    produk_makeup = StringField('Produk Makeup', validators=[DataRequired()])
    shade = StringField('Shade', validators=[DataRequired()])
    skin_color = StringField('Skin Color', validators=[DataRequired()])
    skin_undertone = StringField('Skin Undertone', validators=[DataRequired()])
    add_produk = SubmitField('Tambah')