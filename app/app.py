from flask import Flask, jsonify, render_template, request
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
		with open("test.json") as f:
			d = json.loads(f.read())
		for x in range(len(d["nodes"])):
			d["nodes"][x]["group"] = 1
		with open("test.json", "w") as f:
			f.write(json.dumps(d))

	else:
		pass
	return render_template("index.html")



if __name__ == "__main__":
 	app.run(debug=True)