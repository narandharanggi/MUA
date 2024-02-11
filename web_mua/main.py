# from flask import Flask, render_template, url_for, redirect, request, jsonify
# from flask_mysqldb import MySQL

# app=Flask(__name__)
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'db_mua'
# mysql = MySQL(app)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/recommendation', methods=['GET','POST'])
# def recommendation():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM produk")
#     data_produk = cur.fetchall()
#     cur.execute("SELECT * FROM shade")
#     data_shade = cur.fetchall()
#     cur.execute("SELECT * FROM lokasi")
#     data_lokasi = cur.fetchall()
#     cur.close()

#     if request.method == 'POST':
#         data = [request.json['harga'], request.json['latitude'], request.json['longitude'], request.json['produk']]
#         print(data)
#         return jsonify(data)
#     # if request == 'GET':
#     #     dt = request.get_json()
#     #     print(dt, file=sys.stderr)
#     #     # text = request.args.get('data')
#     #     return jsonify(dt.get('nama_mua'))
    
#     return render_template('recommendation.html', lokasi=data_lokasi, produk=data_produk, shade=data_shade)

# @app.route('/recom')
# def recom():
#     return render_template('browse-ads-2.html')


# if __name__ == '__main__':
#     app.run(debug=True)
