from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    role = db.Column(db.String(25))
    password_hash = db.Column(db.String(500))
    # detail_mua = db.relationship('DetailMua', back_populates='user')
    # mua_items = db.relationship('DetailMua', backref=db.backref('user', lazy=True))

    # @property
    # def password(self):
    #     raise AttributeError('Password is not a readable Attribute')
    
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password=password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __str__(self):
        return '<User %r>' % User.id

class Produk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produk_makeup = db.Column(db.String(200), nullable=False)
    shade = db.Column(db.String(100), nullable=False)
    skin_color = db.Column(db.String(50), nullable=False)
    skin_undertone = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return '<Produk %r>' % Produk.produk_make_up

class Mua(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_mua = db.Column(db.String(100), nullable=False)
    lokasi = db.Column(db.String(100), nullable=False)
    detail_lokasi = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=False)  
    longitude = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'nama_mua': self.nama_mua,
            'alamat' : self.detail_lokasi
        }

    def __str__(self):
        return '<MUA %r>' % self.nama_MUA

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_username_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fk_mua_id = db.Column(db.Integer, db.ForeignKey('mua.id'), nullable=False)
    fk_mua = db.relationship('Mua', backref='mua_rating', lazy=True)
    fk_produk_id = db.Column(db.Integer, db.ForeignKey('produk.id'), nullable=False)
    fk_detail_produk = db.relationship('Produk', backref='produk_rating', lazy=True)
    harga = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def toJson(self):
        return {
            "mua": self.fk_mua.nama_MUA,
            "produk": self.fk_detail_produk.fk_produk.nama_produk,
            "shade": self.fk_detail_produk.fk_shade.shade,
            "harga": self.harga,
            "rating": self.rating
        }