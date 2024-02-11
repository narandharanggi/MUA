from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, relationship
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd
from sqlalchemy import text

USER = 'root'
HOST = 'localhost'
DB_NAME = 'webm'
PASSWORD = ''
database_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}"
engine = create_engine(database_url)
with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    username = Column(String(100), nullable=False)
    role = Column(String(25), nullable=False)
    password_hash = Column(String(500), nullable=False)

class Mua(Base):
    __tablename__ = "mua"
    id = Column(Integer, primary_key=True)
    nama_mua = Column(String(100), nullable=False)
    lokasi = Column(String(100), nullable=False)
    detail_lokasi = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)  
    longitude = Column(Float, nullable=False)

class Produk(Base):
    __tablename__ = "produk"
    id = Column(Integer, primary_key=True)
    produk_make_up = Column(String(200), nullable=False)
    skin_color = Column(String(50), nullable=False)
    skin_undertone = Column(String(50), nullable=False)

class Shade(Base):
    __tablename__ = "shade"
    id = Column(Integer, primary_key=True)
    shade = Column(String(100), nullable=False)

class Detailproduk(Base):
    id = Column(Integer, primary_key=True)
    fk_produk_id = Column(Integer, ForeignKey('produk.id'))
    fk_produk = relationship('Produk', backref='produk_detail', lazy=True)
    fk_shade_id = Column(Integer, ForeignKey('shade.id'))
    fk_shade = relationship('Shade', backref='shade_detail', lazy=True)

database_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
engine = create_engine(database_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

xls = pd.ExcelFile("Data Normalisasi 2.xlsx")
df1 = pd.read_excel(xls, 'Data MUA')
df1 = df1.to_dict('records')
df2 = pd.read_excel(xls, 'Data Produk')
df3 = pd.read_excel(xls, 'Data Shade')

for data in df1:
    new_mua = Mua(**data)
    session.add(new_mua)
    session.commit()