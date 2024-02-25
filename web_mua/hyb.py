import pandas as pd
import regex as re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
nltk.download('punkt')
pd.set_option('display.max_rows',None)
import warnings
warnings.filterwarnings('ignore')
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# ## Data MUA for Memory Based System Recommendation

class ContentBasedFiltering:
    def case_folding(self, text):
        if type(text) == str:
            text = text.lower()
        return text

    def punctuation_removal(self, text):
        if type(text) == str:
            text = re.sub(r'[^\w\s]', '', text)
        return text

    def tokenize(self, text):
        tokens = word_tokenize(text)
        return tokens
        
    def stopwords_removal(self, text):
        stopword_factory = StopWordRemoverFactory()
        stopword_remover = stopword_factory.create_stop_word_remover()
        no_stopword = stopword_remover.remove(text)
        return no_stopword

    def preprocessing(self, text):
        text = self.case_folding(text)
        text = self.punctuation_removal(text)
        text = self.stopwords_removal(text)
        return text

class DataPreprocessing():
    def __init__(self, txt, num):
        #data for recommendation
        dir = os.path.join(basedir, 'static/Data MUA.xlsx')
        file_excel = pd.read_excel(dir)
        file_excel['desc'] = file_excel['produk_makeup'].astype(str) + ' ' + file_excel['shade'].astype(str) + ' ' + file_excel['skin_color'].astype(str) + ' ' + file_excel['skin_undertone'].astype(str)
        file_excel['desc'] = self.preprocessing(file_excel['desc'], query=False)
        self.data = self.kategori_numerik(file_excel, query=False)
        self.raw_data = pd.read_excel(dir)

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
                pre_produk += ' ' + text
            return pre_produk.strip()
    
    def result_pepro(self):
        return self.data, self.raw_data
    
from geopy.geocoders import Photon
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

class Recommendation():
    def __init__(self, produk, alamat, tmp_harga, data_for_model, data_for_user):
        us = self.user_input(produk, alamat, tmp_harga, data_for_model)
        tu = self.testing_user(data_for_model, data_for_user, query=us)
        return tu.to_dict('records')

    def new_data_preparation(data_for_model, data_for_user, query):
        query_data_todict = query.to_dict('index')[0]
        part_of_model = data_for_model.copy()
        part_of_query = part_of_model.loc[part_of_model['nama'] == query['nama'][0]].reset_index()
        part_of_model = part_of_model.reset_index()
        part_of_model = part_of_model.drop(columns='index')
        return query_data_todict, part_of_query, part_of_model


    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize
    from sklearn.metrics.pairwise import cosine_similarity

    def tf_idf_vector(part_of_model, query_data_todict):
        copy_md = part_of_model.copy()
        md = pd.DataFrame(copy_md["desc"])
        md.loc[len(md)] = query_data_todict["desc"]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(md["desc"])
        model = X[:len(part_of_model)]
        query = X[len(part_of_model):]
        return model, query

    from geopy.distance import great_circle
    import math
    def calculate_distance(query_data_todict, part_of_model):
            loc1 = (query_data_todict['latitude'], query_data_todict['longtitude'])
            distance_loc = []
            for i in range(len(part_of_model.index)):
                loc2 = (part_of_model['latitude'][i], part_of_model['longtitude'][i])
                tmp = great_circle(loc1, loc2).km
                value = math.ceil(tmp * 100) / 100
                distance_loc.append(value)
            return distance_loc


    def get_numtext_content(self, query_data_todict, part_of_model):
        tfidf_model, tfidf_query = self.tf_idf_vector(part_of_model, query_data_todict)
        cos_sim = cosine_similarity(tfidf_query, tfidf_model)
        data_sim = cos_sim.reshape(-1,1)
        distance = self.calculate_distance(query_data_todict, part_of_model)
        return data_sim, distance


    from sklearn.preprocessing import StandardScaler

    def get_values(part_of_model):
        tmp_data = part_of_model[['kategori_harga','sim_final']].to_numpy()
        sim_num = cosine_similarity(tmp_data)
        sim_num = np.array([np.mean(p) for p in sim_num])
        return sim_num


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
                    tmp_val.append(part_of_model["sim_num"][j] * part_of_model["sim_final"][j])
            value_mua[i] = np.mean(tmp_val)
        part_of_model = part_of_model.reset_index()
        part_of_model = part_of_model.drop(columns='index')
        return nama_mua, value_mua, part_of_model


    # ## HYBRID FILTERING


    from sklearn.neighbors import NearestNeighbors
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn import preprocessing as pre
    import statistics 


    def testing_user(self, data_for_model, data_for_user, query=None, index_usr=False):
        query_data_todict, part_of_query, part_of_model = self.new_data_preparation(data_for_model, data_for_user, query)
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
            mean_weight[i] = statistics.mean([weight_user[i],  weight_content[i]]) 
        final_res['mean_'] = mean_weight
        final_res = final_res.sort_values(by=['mean_'], ignore_index=True, ascending=False)
        get_user = final_res.groupby("nama").mean_.agg(["mean"])
        list_nama = get_user.index[:10].tolist()
        pivot = part_of_model.copy()
        pivot['mean_'] = mean_weight
        pivot = pivot[pivot.nama.isin(list_nama)].reset_index()
        pivot_ = pivot.groupby("nama_MUA").rating.agg(['count','mean'])
        pivot_['weight'] = pivot.groupby("nama_MUA").mean_.agg(['mean'])
        value_rating = np.zeros(len(pivot_.index), dtype=float)
        for i in range(len(pivot_.index)):
            if pivot_['weight'][i] != 0.0:
                value_rating[i] = pivot_["mean"][i] * pivot_['weight'][i]
            else:
                value_rating[i] = weight_content[i]
        distance = pivot[['nama_MUA','distance']]
        produk = pivot[['nama_MUA', 'sim']]
        final_ = pivot[['nama_MUA', 'sim_num']]
        desc = pivot[['nama_MUA', 'produk_makeup', 'shade', 'skin_color', 'skin_undertone']]
        desc['desc'] = desc['produk_makeup'] + ' - ' + desc['shade'] + ' - ' + desc['skin_color'] + ' - ' + desc['skin_undertone']
        pivot_ = pivot.groupby("nama_MUA").rating.agg(['count','mean'])
        pivot_['nama_MUA'] = desc.groupby('nama_MUA').first().index.to_list()
        pivot_['weight'] = pivot.groupby("nama_MUA").mean_.agg(['mean'])
        pivot_['score'] = value_rating
        pivot_['desc'] = desc.groupby('nama_MUA').agg({'desc': lambda x: list(x)}).reset_index()['desc'].values
        pivot_['distance'] = distance.groupby("nama_MUA").distance.agg(['mean'])
        pivot_['sim'] = produk.groupby("nama_MUA").sim.agg(['mean'])
        pivot_['sim_final'] = final_.groupby("nama_MUA").sim_num.agg(['mean'])
        pivot_ = pivot_.sort_values(by=['score'], ignore_index=True, ascending=False)
        return pivot_

    def user_input(self, product, address, data_for_model):
        column_data = data_for_model.columns
        pre_product = product.split('-')
        empty_data = pd.DataFrame(columns=column_data)
        empty_data['produk_makeup'] = [pre_product[0]]
        empty_data['skin_color'] = [pre_product[1]]
        empty_data['skin_undertone'] = [pre_product[2]]
        empty_data['kategori_harga'] = 1
        empty_data['desc'] = self.cleaning_data([pre_product[0] + ' ' + pre_product[1] + ' ' + pre_product[2]])

        geo = Geolocation()
        pre_address = address.split(',')
        final_address = 'Kecamatan ' + pre_address[0] + ', ' + 'Kabupaten' + pre_address[1] + ',' + pre_address[2]
        print(final_address)
        latlg = geo.get_latitude_longitude(final_address)
        empty_data['latitude'] = [latlg[0]]
        empty_data['longtitude'] = [latlg[1]]

        sim, dis = self.get_numtext_content(empty_data.to_dict('records')[0], data_for_model)
        get_user = data_for_model.copy()
        get_user['sim'] = sim
        get_user['dis'] = dis
        get_user['final'] = get_user['sim']/(get_user['dis'] + 1)
        get_user = get_user.sort_values(by=['final', 'rating'], ascending=[False, False], ignore_index=True)
        get_user = get_user.iloc[[0]]
        return get_user


