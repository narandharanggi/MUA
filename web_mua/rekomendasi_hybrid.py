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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import statistics 
import os
import math
from sklearn.preprocessing import StandardScaler

basedir = os.path.abspath(os.path.dirname(__file__))

class Geolocation():
    import certifi
    import ssl
    import geopy.geocoders
    def __init__(self):
        ctx = self.ssl.create_default_context(cafile=self.certifi.where())
        self.geopy.geocoders.options.default_ssl_context = ctx
        self.geolocator = Photon(user_agent="photon")

    def get_latitude_longitude(self, address):
        self.location = self.geolocator.geocode(address)
        return (self.location.latitude, self.location.longitude)

class DataPreprocessing():
    def __init__(self, txt, num):
        #data for recommendation
        dir = os.path.join(basedir, 'static/Data MUA.xlsx')
        file_excel = pd.read_excel(dir)
        file_excel['desc'] = file_excel['produk_makeup'].astype(str) + ' ' + file_excel['shade'].astype(str) + ' ' + file_excel['skin_color'].astype(str) + ' ' + file_excel['skin_undertone'].astype(str)
        file_excel['desc'] = self.preprocessing(file_excel['desc'], query=False)
        file_excel = file_excel.groupby('no').agg({'nama':'first', 'nama_MUA':'first', 'kategori_harga': 'first', 'latitude':'first', 'longtitude':'first', 'rating':'first','desc':' '.join}).reset_index()
        self.data = self.kategori_numerik(file_excel, query=False)
        self.raw_data = pd.read_excel(dir)

        #query from user
        self.df_query = pd.DataFrame(columns=['no', 'nama', 'nama_MUA', 'produk_makeup', 'skin_color', 'skin_undertone', 'kategori_harga', 'latitude', 'longtitude', 'rating', 'desc'])
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
        return self.df_query, self.data, self.raw_data
    

class Recommendation():
    def __init__(self, part_of_query, part_of_model, raw_data, alamat):
        self.data = part_of_model
        self.raw_data = raw_data
        self.query = part_of_query
        self.location = Geolocation()
        latlg = self.location.get_latitude_longitude(alamat)
        print(latlg)
        self.query['latitude'] = [latlg[0]]
        self.query['longtitude'] = [latlg[1]]
        self.query_data_todict = part_of_query.to_dict('records')[0]
        print(self.query_data_todict)

    def calculate_distance(self):
        loc1 = (self.query_data_todict['latitude'], self.query_data_todict['longtitude'])
        print(loc1)
        distance_loc = []
        for i in range(len(self.data.index)):
            loc2 = (self.data['latitude'][i], self.data['longtitude'][i])
            print(loc2)
            tmp = great_circle(loc1, loc2).km
            value = math.ceil(tmp * 100) / 100
            distance_loc.append(value)
        return distance_loc

    def tf_idf_vector(self):
        copy_md = self.data.copy()
        md = pd.DataFrame(copy_md["desc"])
        md.loc[len(md)] = self.query_data_todict["desc"]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(md["desc"])
        model = X[:len(self.data)]
        query = X[len(self.data):]
        return model, query
    
    def get_numtext_content(self):
        tfidf_model, tfidf_query = self.tf_idf_vector()
        cos_sim = cosine_similarity(tfidf_query, tfidf_model)
        data_sim = cos_sim.reshape(-1,1)
        distance = self.calculate_distance()
        return data_sim, distance

    def get_values(self):
        tmp_data = self.data[['kategori_harga','distance', 'sim']].to_numpy()
        scaler = StandardScaler().fit(tmp_data)
        scaled_data = scaler.transform(tmp_data)
        sim_num = cosine_similarity(scaled_data)
        sim_num = np.array([np.mean(p) for p in sim_num])
        return sim_num

    def value_of_mua(self):
        sim, distance = self.get_numtext_content()
        self.data["sim"] = sim
        self.data["distance"] = distance
        get_user = self.data.copy()
        get_user = get_user.sort_values(by=['sim'], ascending=False, ignore_index=True)
        get_user = get_user.to_dict("records")[0]['nama']
        get_user_value = self.data.copy()
        get_user_value = get_user_value.loc[get_user_value.nama == get_user]
        sim_num = self.get_values()
        self.data["sim_num"] = sim_num
        self.data = self.data.sort_values(by=['nama_MUA'])
        nama_mua = self.data["nama_MUA"].unique()
        value_mua = np.empty(len(nama_mua), dtype=float)

        for i in range(len(nama_mua)):
            tmp_val = []
            for j in range(len(self.data.index)):
                if nama_mua[i] == self.data.nama_MUA[j]:
                    tmp_val.append(self.data["sim_num"][j])
            value_mua[i] = np.mean(tmp_val)
        self.data = self.data.reset_index()
        self.data = self.data.drop(columns='index')
        return nama_mua, value_mua, get_user_value

    def predict(self):
        nama_mua, value_mua, get_user_value = self.value_of_mua()
        pivot = pd.pivot_table(self.data, columns='nama_MUA', index='nama', values='rating', aggfunc='mean', fill_value=0)
        col_model = pivot.columns.tolist()
        val_model = np.array(pivot.values.tolist(), dtype=float)
        nama_user = np.array(pivot.index.tolist())
        pivot_query = pd.pivot_table(get_user_value, columns='nama_MUA', index='nama', values='rating', aggfunc='mean', fill_value=0)
        val_query = pivot_query.values.tolist()
        col_query = pivot_query.columns.tolist()
        feature = np.zeros(len(col_model), dtype=float)
        for i in range(len(col_model)):
            for j in range(len(col_query)):
                if col_model[i] == col_query[j]:
                    feature[i] = val_query[0][j]
                    break
        cos_sim_user = cosine_similarity([feature], val_model)

        weight_user = np.empty(len(self.data), dtype=float)
        for i in range(len(self.data)):
            for j in range(len(nama_user)):
                if self.data["nama"][i] == nama_user[j]:
                    weight_user[i] = cos_sim_user[0][j]

        weight_content = np.empty(len(self.data), dtype=float)
        for i in range(len(self.data)):
            for j in range(len(nama_mua)):
                if self.data["nama_MUA"][i] == nama_mua[j]:
                    weight_content[i] = value_mua[j]
        
        final_res = self.data.copy()
        final_res = final_res[['nama', 'nama_MUA']]
        final_res['user'] = weight_user
        final_res['content'] = weight_content
        
        mean_weight = np.zeros(len(self.data), dtype=float)
        for i in range(len(self.data)):
            mean_weight[i] = statistics.harmonic_mean([weight_user[i],  abs(weight_content[i])])
        final_res['mean_'] = mean_weight
        final_res = final_res.sort_values(by=['mean_'], ignore_index=True, ascending=False)
        get_user = final_res.groupby("nama").mean_.agg(["mean"])
        list_nama = get_user.index[:10].tolist()
        pivot = self.data.copy()
        pivot['mean_'] = mean_weight
        pivot = pivot[pivot.nama.isin(list_nama)].reset_index()
        col_mua_pivot = pd.pivot_table(pivot, columns='nama_MUA', index='nama', values='rating', aggfunc='mean', fill_value=0)
        pivot_ = pivot.groupby("nama_MUA").rating.agg(['count','mean'])
        pivot_['nama_MUA'] = col_mua_pivot.columns.tolist()
        pivot_['weight'] = pivot.groupby("nama_MUA").mean_.agg(['mean'])
        value_rating = np.zeros(len(pivot_.index), dtype=float)
        for i in range(len(pivot_.index)):
            value_rating[i] = (pivot_["mean"][i] * pivot_['weight'][i])
        pivot_['score'] = value_rating
        pivot_['distance'] = pivot.groupby("nama_MUA").distance.agg(['mean'])
        mua_recs = pivot_.sort_values(by=['score', 'distance'], ascending=[False, True], ignore_index=True)
        self.raw_data = self.raw_data[self.raw_data.nama.isin(list_nama)].reset_index()
        self.raw_data = self.raw_data[['no', 'produk_makeup', 'shade', 'skin_color', 'skin_undertone']]
        self.raw_data['desc'] = self.raw_data['produk_makeup'] + ' - ' + self.raw_data['shade'] + ' - ' + self.raw_data['skin_color'] + ' - ' + self.raw_data['skin_undertone']
        self.raw_data = self.raw_data.groupby('no').agg({'desc': lambda x: list(x)}).reset_index()
        # for sm in range(len(mua_recs['mean_cos'])):
        #     tmp_val = math.floor(mua_recs['count'][sm] * mua_recs['mean'][sm] * mua_recs['mean_cos'][sm])
        #     if tmp_val > 5:
        #         tmp_val = 5
        #     elif tmp_val == 0:
        #         tmp_val = 1
        #     tmp_score.append(tmp_val)
        # mua_recs['score'] = tmp_score
        # mua_recs = pd.DataFrame(mua_recs.to_records())
        # mua_recs = mua_recs.sort_values(by=['score', 'distance'], ascending=[False, True], ignore_index=True)
        return mua_recs['nama_MUA'].values.tolist(), mua_recs['mean'].values.tolist(), mua_recs['distance'].values.tolist(), self.raw_data['desc'].to_list(), self.raw_data.index.to_list()
