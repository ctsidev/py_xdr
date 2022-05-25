from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from XDR_Gen import XDR_Gen
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    request_data = request.get_json()
    xdr = XDR_Gen(request_data['PROJECT_ID'], request_data['BASIS'])
    scripts = xdr.generate(request_data['TABLES'])
    return jsonify(scripts)

@app.route('/api/tables')
def tables():
    tables = json.load(open('tables.json', 'r'))
    return jsonify(tables)

if __name__ == "__main__":
    app.run(port=5001)