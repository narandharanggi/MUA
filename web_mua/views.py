from flask import Blueprint, render_template
from .models import User
from . import db


views = Blueprint('views', __name__)

@views.route('/')
def home():
    user = User.query.filter_by(role='admin').first()
    if user:
        return render_template('index.html')
    else:
        new_admin = User()
        new_admin.email = 'admin@gmail.com'
        new_admin.username = 'admin'
        new_admin.role = 'admin'
        new_admin.password_hash = 'scrypt:32768:8:1$hcyAoercNAlOJUCs$b1d5614d394735cb08ea3fc064c837d067a689fc8d11e4c0c79657119dc3ac57f1dd8a0d7762a3aa58e77be0d1496528ffffbb92024eb7302497800b2518b52c'
        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            print(e)

        return render_template('index.html')