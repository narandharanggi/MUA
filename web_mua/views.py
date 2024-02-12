from flask import Blueprint, render_template
from .models import User, Mua, Produk
from werkzeug.security import generate_password_hash
from . import db
import pandas as pd
import os



views = Blueprint('views', __name__)

basedir = os.path.abspath(os.path.dirname(__file__))
dir = os.path.join(basedir, 'static/Data Normalisasi 2.xlsx')
xls = pd.ExcelFile(dir)
df1 = pd.read_excel(xls, 'Data MUA')
df2 = pd.read_excel(xls, 'Data Produk')

def add_mua(data_mua):
    data_mua = data_mua.to_dict('records')
    for data in data_mua:
        mua = Mua(**data)
        db.session.add(mua)
        db.session.commit()

def add_produk(data_produk):
    data_produk = data_produk.to_dict('records')
    for data in data_produk:
        produk = Produk(**data)
        db.session.add(produk)
        db.session.commit()

@views.route('/')
def home():
    user = User.query.filter_by(role='admin').first()
    if user:
        print(df1)
        return render_template('index.html')
    else:
        new_admin = User()
        new_admin.email = 'admin@gmail.com'
        new_admin.username = 'admin'
        new_admin.role = 'admin'
        new_admin.password_hash = generate_password_hash('admin123')
        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            print(e)

        add_mua(df1)
        add_produk(df2)

        return render_template('index.html')