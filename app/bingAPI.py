
import httplib, urllib, base64
from lxml import html
import json
import requests
from bs4 import BeautifulSoup
import re

import numpy as np

# from IPython import embed

class Search_query(object):
    """docstring for Search_query"""
    def __init__(self, query_str=None):
        super(Search_query, self).__init__()
        api_key_file = open("api_key_bing_search.txt", "r") 
        self.api_key = api_key_file.read()
        api_key_file.close()

        self.query_str = query_str

        self.results_dict = dict()
        self.sampelled_pages  = []
        

    def query_bing_search(self, query_str=None, count = 10, offset = 0):
        if query_str is None:
            query_str = self.query_str
            assert query_str is not None, "No query string"
    
        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': self.api_key,
        }

        params = urllib.urlencode({
            # Request parameters
            'q': query_str,
            'count': count,
            'offset': offset,
            'mkt': 'en-us',
            'safesearch': 'Moderate',
        })
        try:
            conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
            conn.request("GET", "/bing/v5.0/search?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            data = json.loads(data) 

            n_result = len(data['webPages']['value'])
            for i in xrange(offset,offset+n_result):
                self.results_dict[i] = data['webPages']['value'][i-offset]

            return data['webPages']['value']
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        print("ERR this should not happen query_bing_search")
        return None

    def web_page_text_second_trial(self, url):
        page_text = ""
        try:
            page = html.fromstring(urllib.urlopen(url).read())
            page_text = page.text_content()

        except Exception as e:
            try:
                url_added_http = "http://"+url
                page = html.fromstring(urllib.urlopen(url_added_http).read())
                page_text = page.text_content()

            except Exception, e:
                print "[INFO] final exception reached, skipping the page"


        page_text = re.sub(r'[^\x00-\x7F]+',' ', page_text)  # filters out weird character
        page_text = re.sub(r'([\t|\n| ])+',' ', page_text)   # filters out consecutive tabs, spaces and new lines
        as_list = str(page_text).split()
        page_text = ' '.join(filter( lambda x: len(x)<30, as_list))
        return (url, page_text)

    def web_page_text(self, url):
        page_text = ""
        try:
            page = requests.get(url)
            html = page.content
            soup = BeautifulSoup(html,"lxml")
            page_text = soup.get_text()
        except Exception as e:
            print ("[INFO] first exception ", url)
            try:
                url_added_http = "http://"+url
                page = requests.get(url_added_http)
                html = page.content
                soup = BeautifulSoup(html,"lxml")
                page_text = soup.get_text()
            except Exception, e:
                print ("[INFO] second exception ", url)
                return self.web_page_text_second_trial(url)


        page_text = re.sub(r'[^\x00-\x7F]+',' ', page_text)  # filters out weird character
        page_text = re.sub(r'([\t|\n| ])+',' ', page_text)
        as_list = str(page_text).split()
        page_text = ' '.join(filter( lambda x: len(x)<30, as_list))
        return (url, page_text)

    def sample(self, n_samples = 35):
        self.sampelled_pages = []
        ids = np.random.random_integers(0,19,10)  # sampling 10 pages from first 20
        ids = np.concatenate((ids, np.random.random_integers(20,99,15) ))
        ids = np.concatenate((ids, np.random.random_integers(100,149,10) ))

        self.query_bing_search(self.query_str, count = 50, offset = 0)
        self.query_bing_search(self.query_str, count = 50, offset = 50)
        self.query_bing_search(self.query_str, count = 50, offset = 100)

        print(len(self.results_dict.keys()))
        print ids

        for i in ids:
            url = self.results_dict[i]['displayUrl']
            text = self.web_page_text(url)
            if text is None:
                print i, "skipped, was None", url
                continue
            # self.sampelled_pages.append((i,url,text))
            self.sampelled_pages.append({'id':i,'url':url,'name':self.results_dict[i]['name'],'snippet':self.results_dict[i]['snippet'], 'text':text}) #(i,url,text))
            

        max_iter = 200
        iteration = 0
        while len(self.sampelled_pages)<n_samples and iteration<max_iter:
            iteration += 1
            print iteration, len(self.sampelled_pages)
            i = np.random.random_integers(0,len(ids))
            # if i not in [j[0] for j in self.sampelled_pages]:
            if i not in [j['id'] for j in self.sampelled_pages]:
                url = self.results_dict[i]['displayUrl']
                text = self.web_page_text(url)
                if text is None:
                    print i, "skipped, was None in while loop", url
                    continue
                # self.sampelled_pages.append((i,url,text))
                self.sampelled_pages.append({'id':i,'url':url,'name':self.results_dict[i]['name'],'snippet':self.results_dict[i]['snippet'], 'text':text}) #(i,url,text))


        return self.sampelled_pages

####################################
# # Usage:

if __name__ == '__main__':
    query = Search_query('smartphone')
    out = query.sample()

# # # out is list of dictionaries with keys id, url, name, snippet, text per each web page 
# # [
# #     {'id':23,
# #     'url':"www.google.com",
# #     'name':"google",
# #     'snippet':"some search engine", 
# #     'text':"Search, Feeling lucky! .. "}
# # ]


# just for the record
# f = open("out","wb")
# f.write(str(out))
# f.close()

# embed()
