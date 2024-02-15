from flask import Blueprint, render_template, flash, request, url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from .forms import MuaForm, ProdukForm
from .models import Mua, Produk, Rating
from . import db
from sqlalchemy.sql import text

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return render_template('index.html')
    return render_template('error.html')

@admin.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if current_user.role == 'admin':
        page = request.args.get('page', 1, type=int)
        page_items = Rating.query.paginate(page=page, per_page=5)
        res_items = []
        for i in Rating.query.paginate(page=page, per_page=5):
            res_items.append(i.toJson())     
        return render_template('admin_rating.html', res_items=res_items, page_items=page_items)
    return render_template('error.html')

@admin.route('/mua',methods=['GET', 'POST'])
@login_required
def mua():
    form = MuaForm()
    if current_user.role == 'admin':
        page = request.args.get('page', 1, type=int)
        items = Mua.query.paginate(page=page, per_page=5)
        if form.validate_on_submit():
            nama_mua = form.nama_mua.data
            lokasi = form.lokasi.data
            detail_lokasi = form.detail_lokasi.data
            latitude = form.latitude.data
            longitude = form.longitude.data

            new_mua = Mua()
            new_mua.nama_mua = nama_mua
            new_mua.lokasi = lokasi
            new_mua.detail_lokasi = detail_lokasi
            new_mua.latitude = latitude
            new_mua.longitude = longitude

            try:
                db.session.add(new_mua)
                db.session.commit()
                flash(f'{nama_mua} berhasil ditambahkan')
                return redirect(url_for('admin.mua'))
            except Exception as e:
                print(e)
                flash('Produk tidak ditambahkan')
        
        return render_template('admin_mua.html', form=form, items=items)

    return render_template('error.html')
        

# @admin.route('/add-mua', methods=['GET', 'POST'])
# @login_required
# def add_mua():
#     form = MuaForm()
#     if current_user.role == 'admin':
#         # search = False
#         # q = request.args.get('q')
#         # if q:
#         #     search = True

#         # page = request.args.get(get_page_parameter(), type=int, default=1)
#         # items = Mua.query
#         # pagination = Pagination(page=page, per_page=2, total=items.count(), search=search, record_name='items')
#         if form.validate_on_submit():
#             nama_mua = form.nama_mua.data
#             alamat = form.alamat.data

#             new_mua = Mua()
#             new_mua.nama_MUA = nama_mua
#             new_mua.alamat = alamat

#             try:
#                 db.session.add(new_mua)
#                 db.session.commit()
#                 flash(f'{nama_mua} berhasil ditambahkan')
#                 return redirect(url_for('admin.mua'))
#             except Exception as e:
#                 print(e)
#                 flash('Produk tidak ditambahkan')
        
#         return redirect(url_for('admin.mua'))

#     return render_template('error.html')

@admin.route('/update_item/<int:item_id>', methods=['GET','POST'])
@login_required
def update_item(item_id):
    if current_user.role == 'admin':
        mua = Mua.query.get(item_id)
        mua.nama_mua = request.form.get('nama_mua', mua.nama_mua)
        mua.lokasi = request.form.get('lokasi', mua.lokasi)
        mua.detail_lokasi = request.form.get('detail_lokasi', mua.detail_lokasi)
        mua.latitude = request.form.get('latitude', mua.latitude)
        mua.longitude = request.form.get('longitude', mua.longitude)
        db.session.commit()
        return redirect(url_for('admin.mua'))
        
    return render_template('error.html')

@admin.route('/delete_item/<int:item_id>', methods=['GET','POST'])
@login_required
def delete_item(item_id):
    if current_user.role == 'admin':
        try:
            item_to_delete = Mua.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            return redirect(url_for('admin.mua'))
        except Exception as e:
            flash('Item tidak dihapus')
        return redirect(url_for('admin.mua'))
        
    return render_template('error.html')

@admin.route('/produk',methods=['GET', 'POST'])
@login_required
def produk():
    form = ProdukForm()
    if current_user.role == 'admin':
        page = request.args.get('page', 1, type=int)
        items = Produk.query.paginate(page=page, per_page=5)
        if form.validate_on_submit():
            produk_makeup = form.produk_makeup.data
            shade = form.shade.data
            skin_color = form.skin_color.data
            skin_undertone = form.skin_undertone.data

            new_produk = Produk()
            new_produk.produk_makeup = produk_makeup
            new_produk.shade = shade
            new_produk.skin_color = skin_color
            new_produk.skin_undertone = skin_undertone

            try:
                db.session.add(new_produk)
                db.session.commit()
                flash(f'{produk_makeup} berhasil ditambahkan')
                return redirect(url_for('admin.produk'))
            except Exception as e:
                print(e)
                flash('Produk tidak ditambahkan')
        
        return render_template('admin_produk.html', form=form, items=items)

    return render_template('error.html')

@admin.route('/update_produk/<int:item_id>', methods=['GET','POST'])
@login_required
def update_produk(item_id):
    if current_user.role == 'admin':
        produk = Produk.query.get(item_id)
        produk.produk_makeup = request.form.get('produk_makeup', produk.produk_makeup)
        produk.shade = request.form.get('shade', produk.shade)
        produk.skin_color = request.form.get('skin_color', produk.skin_color)
        produk.skin_undertone = request.form.get('skin_undertone', produk.skin_undertone)
        db.session.commit()
        return redirect(url_for('admin.produk'))
        
    return render_template('error.html')

@admin.route('/delete_produk/<int:item_id>', methods=['GET','POST'])
@login_required
def delete_produk(item_id):
    if current_user.role == 'admin':
        try:
            item_to_delete = Produk.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            return redirect(url_for('admin.produk'))
        except Exception as e:
            flash('Item tidak dihapus')
        return redirect(url_for('admin.produk'))
        
    return render_template('error.html')