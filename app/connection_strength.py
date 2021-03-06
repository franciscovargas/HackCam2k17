import json
from sklearn.feature_extraction.text import *
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
from sklearn import metrics
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from gensim.models import Word2Vec # (need to do this!)
from scipy import sparse
import numpy as np
import string
import pickle
from IPython import embed



class StemmTokenizer(object):
    """
    At the moment its just stemming. Make to lemminzing later
    """
    def __init__(self):
        self.stemmer = PorterStemmer()

    def stem_tokens(self, tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(self.stemmer.stem(item))
        return stemmed

    def __call__(self, doc):
        # tokens = word_tokenize(doc)
        # tokens = [i for i in tokens if i not in string.punctuation]
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        tokens = word_tokenize(doc.lower().translate(remove_punctuation_map))
        return self.stem_tokens(tokens, self.stemmer)

class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        tokens = word_tokenize(doc)
        tokens = [i for i in tokens if i not in string.punctuation]
        return [self.wnl.lemmatize(t) for t in tokens]



def get_vector_space(docs):
    """
    get td-idf vector space of a all document given their text

    params to play with:
    stopwords : english or None
    smooth_idf : true or false
    tokenizer : stemming
    """
    return TfidfVectorizer(smooth_idf=False, tokenizer=StemmTokenizer(), stop_words='english')
    # return TfidfVectorizer(smooth_idf=False, tokenizer=LemmaTokenizer(), stop_words='english')


def apply_weight(transformer, docs_vectors, filter_keywords):
    """
    bias the document vector towards the desired words/phrases

    Normalize?
    """

    model = Word2Vec.load('brown_model')
    main_word = filter_keywords[0]

    if main_word in model.vocab:
        weights = np.zeros(len(transformer.get_feature_names()))
        i = 0
        for word in transformer.get_feature_names():
            if word in model.vocab:
                weights[i] = model.similarity(main_word, word)
                i = i + 1
            else:
                weights[i] = 0

        # print weights
        # weights = weights / np.linalg.norm(weights)
        # print weights
        weights = np.tile(weights, (1, docs_vectors.shape[0])).reshape(docs_vectors.toarray().shape)
        return sparse.csr_matrix(np.multiply(weights, docs_vectors.toarray()))
    else:
        return docs_vectors



def link_correlation(doc1, doc2):
    """
    Do the 2 documents link to each other?
    How many overlapping hyperlinks?
    Define their correlation with these 2 features
    """
    b1 = 0.7
    b2 = 0.3

    hyperlinks_doc1 = []
    hyperlinks_doc2 = []

    link12 = 0
    link21 = 0

    if (doc1 in hyperlinks_doc2):
        link21 = 1

    if (doc2 in hyperlinks_doc1):
        link12 = 1

    overlapped_links = len(list(set(hyperlinks_doc1).intersection(hyperlinks_doc2))) # overlapping between two documents

    return b1*(link12 + link21) + b2*overlapped_links


def context_correlation(doc1, doc2):
    """
    return correlation between two documents, using their context
    """

    return doc1*doc2.transpose()

def overall_correlation(doc1, doc2):
    """
    return overal correlation. a1 and a2 represent importance in context or hyperlink similarity
    """

    a1 = 0.5
    a2 = 0.5

    return a1*correlation(doc1, doc2) + a2*link_correlation(doc1, doc2)

def correlation_matrix(docs):
    """
    Define matrix where M_ij represent correlation between document i and j
    """

    cr_matrix = np.zeros((docs.shape[0], docs.shape[0]))

    for i in range(docs.shape[0]):
        for j in range(docs.shape[0]):
            cr_matrix[i,j] = context_correlation(docs[i],docs[j])[0,0]

    return cr_matrix

def agg_dist(docs, kmeans):
    """
    Finds intra cluster agregate distance
    for each cluster and sums them up
    as an overal measure of dispersion
    in the clustering.
    """
    agg_d = 0
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    # print docs.shape # 35

    for d in range(docs.shape[0]):
        #print docs[d].toarray().reshape(docs[d].shape[1]).shape # 2382
        #print centroids[d].shape # 2382
        doc = docs[d].toarray().reshape(docs[d].shape[1])
        dist = np.linalg.norm(doc-centroids[labels[d]])
        agg_d += dist

    return agg_d

def counter(docs):
    """
    Return the number of filtrewords in each doc
    """
    vectorizer = CountVectorizer(min_df=1)
    X = vectorizer.fit_transform(docs)
    print vectorizer.get_feature_names()

    return X.toarray()

def choose_k(docs):

    # scores = np.arrange(1,6)

    # for i in range(1,6):
    #     kmeans_model = KMeans(n_clusters=i, random_state=1).fit(docs)
    #     scores[i] = 0 # fix this

    # # use the scores to pick k between 1 and 6

    scores = np.zeros(6-2)
    differences = np.zeros(6-3)
    differences2 = np.zeros(6-4)
    for i in range(2,6):
        kmeans_model = KMeans(n_clusters=i, random_state=1).fit(docs)
        scores[i-2] = agg_dist(docs, kmeans_model) # fix this
 
    for j in range(len(differences)):
        differences[j] = scores[j] - scores[j+1]
 
    for z in range(len(differences2)):
        differences2[z] = differences[z] - differences[z+1]

    return np.argmax(differences2) + 3

def k_cluster(docs):
    """
    Do a clustering between all documents.
    k is chosen automatically (the elbow method)
    """
    # kmeans_model = KMeans(n_clusters=3, random_state=1).fit(docs)
    kmeans_model = KMeans(n_clusters=choose_k(docs), random_state=1).fit(docs)
    # for evaluation
    labels = kmeans_model.labels_
    eval = metrics.silhouette_score(docs, labels, metric='euclidean')
    return kmeans_model

def extract_keywords_doc(kmeans, transformer, docs_vectors, cluster_doc_num, doc):
    """
    Given a cluster and a document, find a suggestion list of keywords for that document to the cluster

    Might wanna do something here about the position/occurece in the tile
    """


    cluster_docs = np.where(km.labels_==cluster_doc_num)[0]
    doc_weights = np.zeros(len(transformer.get_feature_names()))

    for i in range(len(transformer.get_feature_names())):
        for d in cluster_docs:
            if (d != doc):
                doc_weights[i] += docs_vectors[d,i]*docs_vectors[doc,i]

    return doc_weights

def extract_keywords_cluster(kmeans, transformer, docs_vectors, cluster_doc_num):
    """
    Given a cluster, extract a set of keywords/features to show in the graph which essentially defines the cluster
    (Eliminate the query keywords ofcourse)
    """

    cluster_docs = np.where(km.labels_==cluster_doc_num)[0]
    print cluster_docs.shape
    cluster_weights = np.zeros((cluster_docs.shape[0], len(transformer.get_feature_names())))
    i = 0
    for d in cluster_docs:
        cluster_weights[i] = extract_keywords_doc(kmeans, transformer, docs_vectors, cluster_doc_num, d)
        i = i + 1

    return cluster_weights

def save_jasonFile(docs, D, kmeans, names, urls, snippets):
    """
    make a dictionary and save it as a jason file for visualization
    """

    nodes = []
    links = []

    for id in range(len(docs)):
        d = {}
        d["id"] = names[id]
        d["group"] = float( kmeans.labels_[id])
        d["url"] = urls[id]
        d["snippet"] = snippets[id]
        nodes.append(d)

    cr_matrix = correlation_matrix(D)
    # threshold = np.percentile(cr_matrix, 100*((len(kmeans.cluster_centers_) - 1.0)/len(kmeans.cluster_centers_))) 
    threshold = np.percentile(cr_matrix, 90)

    for i in range(len(docs)-1):
        for j in range(i+1,len(docs)):
            if (cr_matrix[i,j] > threshold):
                print(i,j)
                print(names[i], names[j])
                d = {}
                d["source"] = names[i]
                d["target"] = names[j]
                d["value"] = cr_matrix[i,j]
                links.append(d)


    # print nodes
    # print links
    with open("test.json", "wb") as f:
        # embed()
        jsn = json.dumps({"nodes" : nodes, "links" : links}, indent=2)
        f.write(jsn)

    return {"nodes" : nodes, "links" : links}


if __name__ == "__main__":

    with open('sampelled_pages.pkl', 'rb') as f:
        data = pickle.load(f)



    print data[0].keys()
    docs = []
    names = []
    snippets = []
    urls = []
    for d in data:
        names.append(d['name'])
        docs.append(d['text'])
        snippets.append(d['snippet'])
        urls.append(d['url'])

    print len(set(names)) < len(names)

    # docs = ['This is the first run document.',
    # 'This is the second second running document dog.',
    # 'And the third runs ran one dog dog.',
    # 'Is this the first run document dogs?']
    filter_keywords = ['smartphone']
    #
    # #print get_term(docs)
    docs = map(lambda x:(x)[1],docs)
    transformer = get_vector_space(docs)
    D = transformer.fit_transform(docs)
    D = apply_weight(transformer, D, filter_keywords)
    km = k_cluster(D)
    x = save_jasonFile(docs, D, km, names, urls, snippets)
