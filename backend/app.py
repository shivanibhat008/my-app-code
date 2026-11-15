import os
from flask import Flask

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def home():
    return f"<h1>Hello World!!</h1><p>Welcome!!</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
