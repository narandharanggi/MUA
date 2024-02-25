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
    def __init__(self, txt, num, alamat):
        #data for recommendation
        dir = os.path.join(basedir, 'static/Data MUA 2.xlsx')
        file_excel = pd.read_excel(dir)
        file_excel['desc'] = file_excel['produk_makeup'].astype(str) + ' ' + file_excel['shade'].astype(str) + ' ' + file_excel['skin_color'].astype(str) + ' ' + file_excel['skin_undertone'].astype(str)
        file_excel['desc'] = self.preprocessing(file_excel['desc'], query=False)
        self.data = self.kategori_numerik(file_excel, query=False)
        self.raw_data = pd.read_excel(dir)

        #query from user
        self.df_query = pd.DataFrame(columns=['no', 'nama', 'nama_MUA', 'produk_makeup', 'skin_color', 'skin_undertone', 'kategori_harga', 'latitude', 'longtitude', 'rating', 'desc'])
        pre_product = txt[0].split('-')
        harga_val = self.kategori_numerik(file_excel, num, query=True)
        self.df_query['kategori_harga'] = harga_val
        produk_val = []
        for i in range(len(pre_product)):
            produk_val.append(self.preprocessing(pre_product[i], query=True))
        print(produk_val)
        self.df_query['produk_makeup'] = [produk_val[0]]
        self.df_query['skin_color'] = [produk_val[1]]
        self.df_query['skin_undertone'] = [produk_val[2]]
        self.df_query['desc'] = [produk_val[0] + ' ' + produk_val[1] + ' ' + produk_val[2]]

        geo = Geolocation()
        pre_address = alamat.split(',')
        final_address = 'Kecamatan ' + pre_address[0] + ', ' + 'Kabupaten' + pre_address[1] + ',' + pre_address[2]
        print(final_address)
        latlg = geo.get_latitude_longitude(final_address)
        self.df_query['latitude'] = [latlg[0]]
        self.df_query['longtitude'] = [latlg[1]]

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
            return pre_produk
        else:
            pre_produk = ''
            for i in txt:
                text = self.case_folding(i)
                text = self.punctuation_removal()
                text = self.stopwords_removal()
                pre_produk += text
            return pre_produk.strip()
    
    def result_pepro(self):
        return self.df_query, self.data, self.raw_data
    

class Recommendation():
    def __init__(self, part_of_query, part_of_model, raw_data):
        self.data = part_of_model
        self.raw_data = raw_data
        self.query = part_of_query
        # dir = os.path.join(basedir, 'static/Data Normalisasi 2.xlsx')
        # xls = pd.ExcelFile(dir)
        # df1 = pd.read_excel(xls, 'Data MUA')
        # latlg = df1[df1["lokasi"].str.contains(alamat)].reset_index()
        # print(latlg)
        # if len(latlg) != 0:
        #     self.query['latitude'] = [latlg['latitude'][0]]
        #     self.query['longtitude'] = [latlg['longitude'][0]]
        # else:
        #     self.location = Geolocation()
        #     latlg = self.location.get_latitude_longitude('Kecamatan ' + alamat[0] + 'Kabupaten ' + alamat[1])
        #     # print(latlg)
        #     self.query['latitude'] = [latlg[0]]
        #     self.query['longtitude'] = [latlg[1]]
        # self.query_data_todict = part_of_query.to_dict('records')[0]
        print(self.query)
        sim, dis = self.get_numtext_content(self.query.to_dict('records')[0], self.data)
        print(sim)
        get_user = self.data.copy()
        get_user['sim'] = sim
        get_user['dis'] = dis
        get_user['final'] = get_user['sim']/(get_user['dis'] + 1)
        get_user = get_user.sort_values(by=['final', 'rating'], ascending=[False, False], ignore_index=True)
        print(get_user)
        self.query = get_user.iloc[[0]]
        print(self.query)

    def calculate_distance(self, query_data_todict, part_of_model):
        loc1 = (query_data_todict['latitude'], query_data_todict['longtitude'])
        print(loc1)
        distance_loc = []
        for i in range(len(part_of_model.index)):
            loc2 = (part_of_model['latitude'][i], part_of_model['longtitude'][i])
            print(loc2)
            tmp = great_circle(loc1, loc2).km
            value = math.ceil(tmp * 100) / 100
            distance_loc.append(value)
        return distance_loc

    def tf_idf_vector(self, query_data_todict, part_of_model):
        copy_md = part_of_model.copy()
        md = pd.DataFrame(copy_md["desc"])
        md.loc[len(md)] = query_data_todict["desc"]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(md["desc"])
        model = X[:len(part_of_model)]
        query = X[len(part_of_model):]
        return model, query
    
    def get_numtext_content(self, query_data_todict, part_of_model):
        tfidf_model, tfidf_query = self.tf_idf_vector(query_data_todict, part_of_model)
        cos_sim = cosine_similarity(tfidf_query, tfidf_model)
        data_sim = cos_sim.reshape(-1,1)
        distance = self.calculate_distance(query_data_todict, part_of_model)
        return data_sim, distance

    def get_values(self, part_of_model):
        tmp_data = part_of_model[['kategori_harga','sim','distance']].to_numpy()
        sim_num = cosine_similarity(tmp_data)
        sim_num = np.array([np.mean(p) for p in sim_num])
        return sim_num

    def data_preparation(self, data_for_model, query):
        query_data_todict = query.to_dict('index')[0]
        print(query_data_todict)
        # part_of_model = dm[dm.index != user].reset_index()
        part_of_model = data_for_model.copy()
        part_of_query = part_of_model.loc[part_of_model['nama'] == query['nama'][0]].reset_index()
        print('poq',part_of_query)
        # part_of_model.loc[part_of_model['nama'] == user, 'rating'] = 0
        part_of_model = part_of_model.reset_index()
        part_of_model = part_of_model.drop(columns='index')
        return query_data_todict, part_of_query, part_of_model

    def value_of_mua(self, query_data_todict, part_of_model):
        sim, distance = self.get_numtext_content(query_data_todict, part_of_model)
        part_of_model["sim"] = sim
        part_of_model["distance"] = distance
        sf = []
        for i in range(len(part_of_model)):
            sf.append(part_of_model["sim"][i]/(part_of_model["distance"][i] + 1))
        part_of_model["sim_final"] = sf   
        sim_num = self.get_values(part_of_model)
        part_of_model["sim_num"] = sim_num
        part_of_model = part_of_model.sort_values(by=['nama_MUA'])
        nama_mua = part_of_model["nama_MUA"].unique()
        value_mua = np.empty(len(nama_mua), dtype=float)
        for i in range(len(nama_mua)):
            tmp_val = []
            for j in range(len(part_of_model.index)):
                if nama_mua[i] == part_of_model.nama_MUA[j]:
                    tmp_val.append(part_of_model["sim_num"][j] + part_of_model["sim_final"][j])
            value_mua[i] = np.mean(tmp_val)
        part_of_model['total_mua'] = part_of_model["sim_num"] + part_of_model["sim_final"]
        part_of_model = part_of_model.reset_index()
        part_of_model = part_of_model.drop(columns='index')
        return nama_mua, value_mua, part_of_model

    def predict(self):
        query_data_todict, part_of_query, part_of_model = self.data_preparation(self.data, self.query)
        nama_mua, value_mua, part_of_model = self.value_of_mua(query_data_todict, part_of_model)
        pivot = pd.pivot_table(part_of_model, columns='nama_MUA', index='nama', values='rating', aggfunc='mean', fill_value=0)
        col_model = pivot.columns.tolist()
        val_model = np.array(pivot.values.tolist(), dtype=float)
        nama_user = np.array(pivot.index.tolist())
        pivot_query = pd.pivot_table(part_of_query, columns='nama_MUA', index='nama', values='rating', aggfunc='mean', fill_value=0)
        val_query = pivot_query.values.tolist()
        col_query = pivot_query.columns.tolist()
        feature = np.zeros(len(col_model), dtype=float)
        for i in range(len(col_model)):
            for j in range(len(col_query)):
                if col_model[i] == col_query[j]:
                    feature[i] = val_query[0][j]
                    break
        cos_sim_user = cosine_similarity([feature], val_model)

        weight_user = np.empty(len(part_of_model), dtype=float)
        for i in range(len(part_of_model)):
            for j in range(len(nama_user)):
                if part_of_model["nama"][i] == nama_user[j]:
                    weight_user[i] = cos_sim_user[0][j]
            
        weight_content = np.empty(len(part_of_model), dtype=float)
        for i in range(len(part_of_model)):
            for j in range(len(nama_mua)):
                if part_of_model["nama_MUA"][i] == nama_mua[j]:
                    weight_content[i] = value_mua[j]
            
        final_res = part_of_model.copy()
        final_res = final_res[['nama', 'nama_MUA']]
        final_res['user'] = weight_user
        final_res['content'] = weight_content

        mean_weight = np.zeros(len(part_of_model), dtype=float)
        for i in range(len(part_of_model)):
            mean_weight[i] = statistics.harmonic_mean([weight_user[i],  weight_content[i]]) 
        final_res['mean_'] = mean_weight
        final_res = final_res.sort_values(by=['mean_'], ignore_index=True, ascending=False)
        get_user = final_res.groupby("nama").mean_.agg(["mean"])
        list_nama = get_user.index[:10].tolist()
        pivot = part_of_model.copy()
        pivot['mean_'] = mean_weight
        pivot = pivot[pivot.nama.isin(list_nama)].reset_index()
        distance = pivot[['nama_MUA','distance']]
        produk = pivot[['nama_MUA', 'sim']]
        final_ = pivot[['nama_MUA', 'sim_final']]
        desc = pivot[['nama_MUA', 'produk_makeup', 'shade', 'skin_color', 'skin_undertone']]
        desc['desc'] = desc['produk_makeup'] + ' - ' + desc['shade'] + ' - ' + desc['skin_color'] + ' - ' + desc['skin_undertone']
        pivot_ = pivot.groupby("nama_MUA").rating.agg(['count','mean'])
        pivot_['nama_MUA'] = desc.groupby('nama_MUA').first().index.to_list()
        pivot_['weight'] = pivot.groupby("nama_MUA").mean_.agg(['mean'])
        pivot_['score'] = pivot_["mean"] * pivot_['weight']
        pivot_['desc'] = desc.groupby('nama_MUA').agg({'desc': lambda x: list(x)}).reset_index()['desc'].values
        pivot_['distance'] = distance.groupby("nama_MUA").distance.agg(['mean'])
        pivot_['distance'] = [math.floor(x) for x in pivot_['distance']]
        pivot_['sim'] = produk.groupby("nama_MUA").sim.agg(['mean'])
        pivot_['sim_final'] = final_.groupby("nama_MUA").sim_final.agg(['mean'])
        pivot_ = pivot_.sort_values(by=['score'], ignore_index=True, ascending=False)
        return pivot_['nama_MUA'].values.tolist(), pivot_['mean'].values.tolist(), pivot_['distance'].values.tolist(), pivot_['desc'].values.tolist(), pivot_.index.to_list()
