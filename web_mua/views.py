from flask import Blueprint, render_template
from .models import User, Mua, Produk, Rating
from werkzeug.security import generate_password_hash
from . import db
import pandas as pd
import os
import re
from sqlalchemy.sql import text, func
from operator import itemgetter



views = Blueprint('views', __name__)

basedir = os.path.abspath(os.path.dirname(__file__))
dir = os.path.join(basedir, 'static/Data Normalisasi 2.xlsx')
dir_rating = os.path.join(basedir, 'static/Data MUA 2 - Harga Asli.xlsx')
xls = pd.ExcelFile(dir)
df1 = pd.read_excel(xls, 'Data MUA')
df2 = pd.read_excel(xls, 'Data Produk')

xls_rating = pd.read_excel(dir_rating)

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

def camel_to_snake(camel_case):
    """
    Convert a camelCase string to snake_case.
    """
    # Insert an underscore before any uppercase letters
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '', camel_case)
    # Convert the string to lowercase
    snake_case = snake_case.lower()
    # Capitalize the first letter of each word
    snake_case = snake_case.title()
    return snake_case

def add_rating(data_rating):
    data_rating = data_rating.to_dict('records')
    for data in data_rating:
        mua = Mua.query.filter_by(nama_mua=data['nama_MUA']).first()
        user = User.query.filter_by(username=data['nama'].split()[0].lower()).first()
        if user is None:
            new_user = User()
            new_user.email = ''.join(data['nama'].split()).lower() + '@gmail.com'
            new_user.username = data['nama'].split()[0].lower()
            new_user.role = 'user'
            new_user.password_hash = generate_password_hash(data['nama'].split()[0].lower())
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        produk_makeup = camel_to_snake(data['produk_makeup'])
        shade = camel_to_snake(data['shade'])
        skin_color = camel_to_snake(data['skin_color'])
        skin_undertone = camel_to_snake(data['skin_undertone']) 
        produk = Produk.query.filter(
                        Produk.produk_makeup.contains(produk_makeup),
                        Produk.shade.contains(shade),
                        Produk.skin_color.contains(skin_color),
                        Produk.skin_undertone.contains(skin_undertone)).first()
        if produk is None:
            new_produk = Produk()
            new_produk.produk_makeup = produk_makeup
            new_produk.shade = shade
            new_produk.skin_color = skin_color
            new_produk.skin_undertone = skin_undertone
            db.session.add(new_produk)
            db.session.commit()
            produk = new_produk

        new_rating = Rating()
        new_rating.fk_username_id = user.id
        new_rating.fk_mua_id = mua.id
        new_rating.fk_produk_id = produk.id
        new_rating.harga = int(data['kategori_harga'])
        new_rating.rating = data['rating']
        db.session.add(new_rating)
        db.session.commit()

@views.route('/', methods=['GET', 'POST'])
def home():
    mua = Mua.query.first() 
    user = User.query.filter_by(role='admin').first()
    rating = Rating.query.first()
    if user:
        if mua is None:
            add_mua(df1)
        if rating is None:
            add_rating(xls_rating)
    elif user is None:
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
        if mua is None:
            add_mua(df1)
        if rating is None:
            add_rating(xls_rating)
    mua_items = Mua.query.limit(10)
    mua_rating = []
    for data in mua_items:
        print(data.to_dict())
        rating = Rating.query.with_entities(func.floor(func.avg(Rating.rating))).filter(Rating.fk_mua_id == data.id).all()
        pr = []
        for j in Rating.query.filter_by(fk_mua_id = data.id).all():
            merge = ''
            produk = j.toJson()['produk']
            shade = j.toJson()['shade']
            skin_color = j.toJson()['skin_color']
            skin_undertone = j.toJson()['skin_undertone']
            merge += produk + '-' + shade + '-' + skin_color + '-' + skin_undertone
            pr.append(merge)
        p = {
                'id' : data.id,
                'nama_mua': data.nama_mua,
                'lokasi': data.detail_lokasi,
                'rating': rating[0][0],
                'str_rating': '(' + str(rating[0][0]) + ')',
                'produk': pr
            }
        mua_rating.append(p)
    mua_rating = sorted(mua_rating, key=itemgetter('rating'), reverse=True)
    return render_template('index.html', mua_rating=mua_rating)