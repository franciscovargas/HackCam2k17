import gensim
import logging
from nltk.corpus import brown

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = brown.sents()
model = gensim.models.Word2Vec(sentences, min_count=1)
model.save('brown_model')
