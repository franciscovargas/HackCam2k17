from flask import Flask, jsonify, render_template, request
from bingAPI import Search_query
from connection_strength import *
import json

app = Flask(__name__)

@app.route('/graph_data')
def get_json():
    d = json.loads(open("test.json").read())
    return jsonify(d)

@app.route('/main', methods=['GET', 'POST'])
def render_graph():
    if request.method == 'POST':
        print "POST"
        data = request.form["data"]
        print data, "DATA"
        query = Search_query(data)
        out = query.sample()

        # print data[0].keys()
        docs = []
        names = []
        snippets = []
        urls = []
        for d in out:
            names.append(d['name'])
            docs.append(d['text'])
            snippets.append(d['snippet'])
            urls.append(d['url'])

        print len(set(names)) < len(names)

        # docs = ['This is the first run document.',
        # 'This is the second second running document dog.',
        # 'And the third runs ran one dog dog.',
        # 'Is this the first run document dogs?']
        filter_keywords = [data]
        #
        # #print get_term(docs)
        docs = map(lambda x:(x)[1],docs)
        transformer = get_vector_space(docs)
        D = transformer.fit_transform(docs)
        D = apply_weight(transformer, D, filter_keywords)
        km = k_cluster(D)
        x = save_jasonFile(docs, D, km, names, urls, snippets)
        

        print len(data)
        print("data: ",data)
        with open("test.json") as f:
            d = json.loads(f.read())
  
        with open("test.json", "w") as f:
            f.write(json.dumps(d))

    else:
        pass
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)