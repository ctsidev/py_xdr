from flask import Flask, jsonify, request
from flask_cors import CORS
from XDR_Gen import XDR_Gen

app = Flask(__name__)
CORS(app)

@app.route("/api/dump", methods=['POST'])
def dump():
    request_data = request.get_json()
    xdr = XDR_Gen(request_data['PROJECT_ID'], request_data['BASIS'])
    scripts = xdr.generate(request_data['TABLES'])
    return jsonify(scripts)


if __name__ == "__main__":
    app.run(debug=True, port=8000)