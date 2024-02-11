from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, Form
from wtforms.validators import DataRequired, length, NumberRange

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
    alamat = StringField('Alamat', validators=[DataRequired()])
    add_mua = SubmitField('Tambah')

class ProdukForm(FlaskForm):
    nama_produk = StringField('Nama Produk', validators=[DataRequired()])
    kategori_produk = StringField('Kategori', validators=[DataRequired()])
    shade_produk = StringField('Shade Produk', validators=[DataRequired()])
    add_produk = SubmitField('Tambah')

class SearchForm(FlaskForm):
    search = StringField('Cari MUA')
    submit = SubmitField('Cari')