from flask import Blueprint, render_template, flash, request, url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from .forms import MuaForm, ProdukForm
from .models import Mua, Produk
from . import db
from sqlalchemy.sql import text

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return render_template('index.html')
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
            alamat = form.alamat.data

            new_mua = Mua()
            new_mua.nama_MUA = nama_mua
            new_mua.deskripsi = 'Hello'
            new_mua.alamat = alamat

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
        mua.nama_MUA = request.form.get('nama_mua', mua.nama_MUA)
        mua.alamat = request.form.get('alamat', mua.alamat)
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
            nama_produk = form.nama_produk.data
            kategori_produk = form.kategori_produk.data
            shade_produk = form.shade_produk.data

            new_produk = Produk()
            new_produk.nama_produk = nama_produk
            new_produk.kategori_produk = kategori_produk
            new_produk.shade = shade_produk

            try:
                db.session.add(new_produk)
                db.session.commit()
                flash(f'{nama_produk} berhasil ditambahkan')
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
        produk.nama_produk = request.form.get('nama_produk', produk.nama_produk)
        produk.kategori_produk = request.form.get('kategori_produk', produk.kategori_produk)
        produk.shade = request.form.get('shade', produk.shade)
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