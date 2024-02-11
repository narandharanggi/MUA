from geopy.geocoders import Photon
from geopy.distance import great_circle
import pandas as pd
import regex as re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
import os
import math
from sklearn.preprocessing import StandardScaler

basedir = os.path.abspath(os.path.dirname(__file__))

class Geolocation():
    def __init__(self):
        self.geolocator = Photon(user_agent="geoapiExercises")

    def get_latitude_longitude(self, address):
        self.location = self.geolocator.geocode(address)
        return (self.location.latitude, self.location.longitude)

class DataPreprocessing():
    def __init__(self, txt, num):
        #data for recommendation
        dir = os.path.join(basedir, 'static/Data MUA.xlsx')
        file_excel = pd.read_excel(dir)
        file_excel['desc'] = file_excel['kategori_produk'].astype(str) + ' ' + file_excel['produk_makeup'].astype(str) + ' ' + file_excel['shade'].astype(str)
        file_excel['desc'] = self.preprocessing(file_excel['desc'], query=False)
        file_excel = file_excel.groupby('no').agg({'nama':'first', 'nama_MUA':'first', 'kategori_harga': 'first', 'latitude':'first', 'longtitude':'first', 'rating':'first','desc':' '.join}).reset_index()
        self.data = self.kategori_numerik(file_excel, query=False)

        #query from user
        self.df_query = pd.DataFrame(columns=['nama', 'nama_MUA', 'kategori_harga', 'latitude', 'longtitude', 'rating', 'desc'])
        harga_val = self.kategori_numerik(file_excel, num, query=True)
        self.df_query['kategori_harga'] = harga_val
        produk_val = self.preprocessing(txt, query=True)
        self.df_query['desc'] = [produk_val]

    def case_folding(self, txt):
        self.text = txt
        if type(self.text) == str:
            self.text = self.text.lower()
        return self.text

    def punctuation_removal(self):
        if type(self.text) == str:
            self.text = re.sub(r'[^\w\s]', '', self.text)
            self.text = re.sub(r"\s+", " ", self.text)
        return self.text

    def tokenize(self, txt):
        self.tokens = word_tokenize(txt)
        return self.tokens
        
    def stopwords_removal(self):
        stopword_factory = StopWordRemoverFactory()
        stopword_remover = stopword_factory.create_stop_word_remover()
        no_stopword = stopword_remover.remove(self.text)
        return no_stopword
    
    def kategori_numerik(self, filename, harga=None, query=False):
        if query == False:
            harga_labels = LabelEncoder()
            harga_labels = harga_labels.fit(filename['kategori_harga'])
            harga_labels.classes_ = np.array(['Murah', 'Sedang', 'Mahal'])
            filename['kategori_harga'] = harga_labels.transform(filename['kategori_harga'])
            return filename
        else:
            if int(harga) <= 150:
                tmp_harga = 'Murah'
            elif int(harga) > 150 and int(harga) <= 250:
                tmp_harga = 'Sedang'
            elif int(harga) > 250:
                tmp_harga = 'Mahal'
            harga_labels = LabelEncoder()
            harga_labels = harga_labels.fit(filename['kategori_harga'])
            harga_labels.classes_ = np.array(['Murah', 'Sedang', 'Mahal'])
            kategori_harga = harga_labels.transform([[tmp_harga]])
            return kategori_harga

    def preprocessing(self, txt, query=False):
        if query == False:
            pre_produk = []
            for i in txt:
                text = self.case_folding(i)
                text = self.punctuation_removal()
                text = self.stopwords_removal()
                pre_produk.append(text)
        else:
            pre_produk = ''
            for i in txt:
                text = self.case_folding(i)
                text = self.punctuation_removal()
                text = self.stopwords_removal()
                pre_produk += ' ' + text
        return pre_produk
    
    def result_pepro(self):
        return self.df_query, self.data
    

class Recommendation():
    def __init__(self, query, data, alamat):
        self.data = data
        self.query = query
        self.location = Geolocation()
        latlg = self.location.get_latitude_longitude(alamat)
        self.query['latitude'] = [latlg[0]]
        self.query['longtitude'] = [latlg[1]]
        self.get_content_num_values()

    def calculate_distance(self):
        loc1 = (self.query['latitude'][0], self.query['longtitude'][0])
        distance_loc = []
        for i in range(len(self.data)):
            loc2 = (self.data['latitude'][i], self.data['longtitude'][i])
            tmp = great_circle(loc1, loc2).km
            value = math.ceil(tmp * 100) / 100
            distance_loc.append(value)
        return distance_loc

    def cos_sim_(self):
        max_features = 1000

        # calc TF vector
        prop_dc = self.data["desc"].copy()
        prop_dc[len(prop_dc.index)+1] = self.query['desc'][0]
        cvect = CountVectorizer(max_features=max_features)
        TF_vector = cvect.fit_transform(prop_dc)

        # normalize TF vector
        normalized_TF_vector = normalize(TF_vector, norm='l1', axis=1)

        # calc IDF
        tfidf = TfidfVectorizer(max_features=max_features, smooth_idf=False)
        tfidf.fit_transform(prop_dc)
        IDF_vector = tfidf.idf_

        # hitung TF x IDF sehingga dihasilkan TFIDF matrix / vector
        tfidf_mat = normalized_TF_vector.multiply(IDF_vector).toarray()
        return tfidf_mat
    
    def get_content_num_values(self):
        #content
        tfidf_mat = self.cos_sim_()
        db_doc = tfidf_mat[:len(self.data)]
        query = tfidf_mat[len(self.data):]
        cos_sim = cosine_similarity(query, db_doc)
        self.data['sim'] = cos_sim.reshape(-1,1)

        #numeric value
        self.data['distance'] = self.calculate_distance()
        tmp_data = self.data[['kategori_harga','distance']].to_numpy()
        scaler = StandardScaler().fit(tmp_data)
        scaled_data = scaler.transform(tmp_data)
        qd = [[self.query['kategori_harga'].values[0], 1.0]]
        scaled_qd = scaler.transform(qd)
        sim_num = np.empty(len(self.data), dtype=float)
        for j in range(len(self.data)):
            sim_num[j] = np.array(cosine_similarity(scaled_qd, [scaled_data[j]]))
        self.data['sim_num'] = sim_num
        self.data = self.data.sort_values(by=['sim_num'], ascending=False, ignore_index=True)
        val_total_sim = self.data[['sim', 'sim_num']]
        self.data['total_sim'] = val_total_sim.mean(axis=1)
        self.data = self.data.sort_values(by=['total_sim'], ignore_index=True)

    def pre_hybrid(self):
        data_hyb = self.data.copy()
        data_hyb = data_hyb[['total_sim']]
        data_hyb ['nama_MUA'] = self.data['nama_MUA']
        data_hyb ['rating'] = self.data['rating'].astype(float)
        data_hyb ['nama'] = self.data['nama']
        pv_dhb = pd.pivot_table(data_hyb, columns='nama_MUA', values='total_sim', aggfunc='mean')
        list_sim = pv_dhb.values.tolist()[0]
        pv_dhb2 = pd.pivot_table(data_hyb, columns='nama_MUA', index='nama', values='rating', fill_value=0)
        list_nama = pv_dhb2.index.tolist()
        nes_sim_to_pv = []
        for x in range(len(pv_dhb2)):
            index = 0
            sim_to_pv = []
            for j in list_sim:
                if pv_dhb2.values[x][index] == 0:  
                    sim_to_pv.append(j)
                else:
                    sim_to_pv.append(float(pv_dhb2.values[x][index]))
                index += 1
            nes_sim_to_pv.append(sim_to_pv)
        return nes_sim_to_pv, list_nama

    def predict(self):
        dc, nama = self.pre_hybrid()
        knn = NearestNeighbors(metric='cosine', algorithm='brute')
        knn.fit(dc)
        distances, indices = knn.kneighbors(dc, n_neighbors=15)
        index_user_query = nama.index(self.data['nama'].values[0])
        get_indices = []
        for z in indices:
            if index_user_query in z.tolist():
                get_indices = z.tolist()
                break
        list_nama = []
        for ln in get_indices:
            list_nama.append(nama[ln])
        pivot_colab = self.data.copy()
        pivot_colab = pivot_colab[pivot_colab.nama.isin(list_nama)].reset_index()
        tmp_cos = np.empty(len(pivot_colab), dtype=float)
        for j in range(len(pivot_colab.nama)):
            for y in range(len(list_nama)):
                if pivot_colab.nama[j] == list_nama[y]:
                    tmp_cos[j] = distances[1][:].tolist()[y]
        pivot_colab['cos'] = tmp_cos
        mua_recs = pivot_colab.groupby("nama_MUA").rating.agg(['count','mean'])
        mua_recs['mean_cos'] = pivot_colab.groupby("nama_MUA").cos.agg(['mean'])
        mua_recs['distance'] = pivot_colab.groupby("nama_MUA").distance.agg(['mean'])
        tmp_score = []
        for sm in range(len(mua_recs['mean_cos'])):
            tmp_val = math.floor(mua_recs['count'][sm] * mua_recs['mean'][sm] * mua_recs['mean_cos'][sm])
            if tmp_val > 5:
                tmp_val = 5
            elif tmp_val == 0:
                tmp_val = 1
            tmp_score.append(tmp_val)
        mua_recs['score'] = tmp_score
        mua_recs = pd.DataFrame(mua_recs.to_records())
        mua_recs = mua_recs.sort_values(by=['score', 'distance'], ascending=[False, True], ignore_index=True)
        return mua_recs['nama_MUA'].values.tolist(), mua_recs['score'].values.tolist(), mua_recs['distance'].values.tolist()
