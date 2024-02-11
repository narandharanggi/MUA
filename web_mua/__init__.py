from flask import Flask, render_template
# from flask_mysqldb import MySQL
import pymysql
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import warnings
warnings.filterwarnings('ignore')


db = SQLAlchemy()

def create_db(host, user, password):
    
    # Initializing connection
    db = pymysql.connections.Connection(
        host=host,
        user=user,
        password=password
    )
    
    # Creating cursor object
    cursor = db.cursor()
    
    # Executing SQL query
    cursor.execute("CREATE DATABASE IF NOT EXISTS mua_web")
    cursor.execute("SHOW DATABASES")
    
    # Displaying databases
    for databases in cursor:
        print(databases)
    
    # Closing the cursor and connection to the database
    cursor.close()
    db.close()

def create_app():
    app = Flask(__name__)
    USER = 'root'
    HOST = 'localhost'
    DB_NAME = 'mua_web'
    PASSWORD = ''
    SECRET_KEY = os.urandom(32)
    # app.config['SECRET_KEY'] = 'hbnwdvbn ajnbsjn ahe'
    # app.config['MYSQL_HOST'] = 'localhost'
    # app.config['MYSQL_USER'] = 'root'
    # app.config['MYSQL_PASSWORD'] = ''
    # app.config['MYSQL_DB'] = 'db_mua'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
    # Disable modification tracking
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html')

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get((int(id)))

    from .views import views
    from .user import user
    from .admin import admin
    from .models import User

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        create_db(HOST, USER, PASSWORD)
        db.create_all()

    return app

