from flask import Flask
from flask import jsonify
from flask import render_template
import json

app = Flask(__name__)

@app.route('/graph_data')
def get_json():
    d = json.loads(open("test.json").read())
    return jsonify(d)

@app.route('/main')
def render_graph():
	return render_template("index.html")



if __name__ == "__main__":
 	app.run(debug=True)