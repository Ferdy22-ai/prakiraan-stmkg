# proxy.py
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/bmkg")
def bmkg_proxy():
    try:
        url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=36.71.01.1003"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)})
