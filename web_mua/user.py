from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from .forms import LoginForm, SignUpForm, SearchForm
from .models import User, Mua, Produk, Rating
from . import db
from .rekomendasi_hybrid import DataPreprocessing, Recommendation
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import text
import json

user = Blueprint('user', __name__)

@user.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user:
            if user.verify_password(password=password):
                login_user(user)
                if current_user.role == 'admin':
                    return redirect('/admin')
                else:
                    return redirect('/user')
            else:
                flash('Email atau Password salah')
        else:
            flash('Akun tidak ada, silakan Daftar terlebih dahulu')

    return render_template('login.html', form=form)

@user.route('/sign-up', methods=['GET','POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:
            new_user = User()
            new_user.email = email
            new_user.username = username
            new_user.role = 'user'
            new_user.password_hash = generate_password_hash(password2)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Akun berhasil dibuat', 'Anda dapat login sekarang')
                return redirect('/user/login')
            except Exception as e:
                print(e)
                flash('Tidak bisa membuat akun, Email sudah tidak tersedia')
            
            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''

    return render_template('signup.html', form=form)

@user.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')

@user.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.role == 'user':
        mua_items = Mua.query.limit(5)
        return render_template('index_user.html', mua_items=mua_items)
    return render_template('error.html')

@user.route('/list-mua', methods=['GET', 'POST'])
@login_required
def list_mua():
    if current_user.role == 'user':
        page = request.args.get('page', 1, type=int)
        mua_items = Mua.query.paginate(page=page, per_page=10)
        return render_template('list_mua.html', mua_items=mua_items)
    return render_template('error.html')

@user.route('/search', methods=['GET','POST'])
@login_required
def search():
    if current_user.role == 'user':
        mua_items = Mua.query.all()
        results = []
        for mi in mua_items:
            results.append(mi.to_dict()['nama_mua'])
        text = request.args['searchText']
        result = [c for c in results if str(text).lower() in c.lower()]
        print(result)
        return json.dumps({"results":result})


@user.route('/rekomendasi', methods=['GET', 'POST'])
@login_required
def rekomendasi():
    if current_user.role == 'user':
        produk_items = Produk.query.with_entities(Produk.produk_makeup).distinct()
        if request.method == 'POST':  
            alamat = request.form.get('alamat')
            harga = request.form.get('harga')
            produk = request.form.getlist('produk[]')
            prepro = DataPreprocessing(produk, harga)
            query, data = prepro.result_pepro()
            prediciton, rating, distance = Recommendation(query, data, alamat).predict()
            ls_alamat = []
            ls_deskripsi = []
            print(prediciton)
            for x in prediciton:
                result_set = Mua.query.filter_by(nama_MUA=prediciton[0]).first()
                ls_alamat.append(result_set.alamat)
                ls_deskripsi.append(result_set.deskripsi)
            return jsonify({'nama_mua':prediciton, 'alamat':ls_alamat, 'deskripsi':ls_deskripsi, 'rating':rating, 'jarak':distance})
        return render_template('rekomendasi.html', produk_items=produk_items)
    return render_template('error.html')

@user.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if current_user.role == 'user':
        mua_items = Mua.query
        produk_items = Produk.query 
        page = request.args.get('page', 1, type=int)
        res_items = Rating.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=5)
        # prod = Produk.query().query().filter_by(detail_mua=res_items.id)

        # muaList = []
        # produkList = []
        # harga = []
        # rating = []
        # for item in res_items:
        #     muaList.append(item.mua_id)
        #     produkList.append(item.produk_id)
        #     harga.append(item.harga)
        #     rating.append(item.rating)
        
        # print(muaList)
        # nama_mua = []
        # for ml in muaList:
        #     res_mua = Mua.query.get(ml)
        #     print(res_mua)
        #     nama_mua.append(res_mua.nama_MUA)
        
        # nama_produk = []
        # nama_shade = []
        # for pl in produkList:
        #     res_pro = Produk.query.get(pl)
        #     nama_produk.append(res_pro.nama_produk)
        #     nama_shade.append(res_pro.shade)
        # # produk = Produk.query.filter_by(id=items.produk_id)
        # # res_produk = [r for r in produk]
        # print(muaList)
        # print(produkList)       
        return render_template('rating.html', mua_items=mua_items, produk_items=produk_items, res_items=res_items)
    return render_template('error.html')

# @user.route('/read-rating', methods=['GET', 'POST'])
# @login_required
# def read_rating():
#     if current_user.role == 'user':
#         if request.method == 'POST':
#             page = request.args.get('page', 1, type=int)
#             # if page == None:
#             #     page = 1
#             # limit = 5
#             # limit_start = (page - 1) * limit
#             tasks = []
#             # total_record = DetailMua.query.filter_by(user_id=current_user.id).count()
#             # sum_of_page = math.ceil(total_record/limit)
#             # sum_of_number = 1

#             # # start_number
#             # if page > limit:
#             #     start_number = page-sum_of_number
#             # else:
#             #     start_number = 1

#             # # end_number
#             # if page < (sum_of_page - sum_of_number):
#             #     end_number = page + sum_of_number
#             # else:
#             #     end_number = sum_of_page

#             for ri in DetailMua.query.filter_by(user_id=current_user.id).all():
#                 tasks.append(ri.toJson())
#             return jsonify(tasks)

@user.route('/form-rating', methods=['GET', 'POST'])
@login_required
def form_rating():
    if current_user.role == 'user':
        if request.method == 'POST':  
            list_produk = request.form.getlist('produk[]')
            list_shade = request.form.getlist('shade[]')
            user_id = current_user.id
            mua = Mua.query.filter_by(nama_MUA=request.form.get('nama_mua')).first()
            harga = request.form.get('harga')
            rating = request.form.get('rating')
            if len(list_produk) > 1:
                for i in range(len(list_produk)):
                    produk = Produk.query.filter(
                        Produk.nama_produk.contains(list_produk[i]),
                        Produk.shade.contains(list_shade[i]))
                    new_rating = Rating()
                    new_rating.user_id = user_id
                    new_rating.mua_id = mua.id
                    new_rating.produk_id = produk.id
                    new_rating.harga = harga
                    new_rating.rating = rating

                    try:
                        db.session.add(new_rating)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        flash('Rating tidak ditambahkan')
            else:
                print(list_produk[0])
                produk = Produk.query.filter(
                        Produk.nama_produk == list_produk[0],
                        Produk.shade == list_shade[0]).first()
                print(produk)
                new_rating = Rating()
                new_rating.user_id = user_id
                new_rating.mua_id = mua.id
                new_rating.produk_id = produk.id
                new_rating.harga = harga
                new_rating.rating = rating

                try:
                    db.session.add(new_rating)
                    db.session.commit()
                    return redirect(url_for('user.rating'))
                except Exception as e:
                    print(e)
                    flash('Rating tidak ditambahkan')
            return redirect(url_for('user.rating'))
    return render_template('error.html')

# @user.route('/read-rating', methods=['GET', 'POST'])
# @login_required
# def read_rating():
#     if current_user.role == 'user':
#         items = DetailMua.query.filter_by(user_id=current_user.id)
#         produk = Produk.query.filter_by(produk_id=items.produk_id)
#         res_items = [r for r, in items]
#         res_produk = [r for r in produk]
#         print(res_items)
#         return render_template('read-rating.html', items = items, produk=produk)
#     return render_template('error.html')
