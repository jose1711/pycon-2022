from http import HTTPStatus

import requests
from flask import Flask, jsonify, redirect, url_for

# Create the Flask application
app = Flask(__name__)

BLOOMREACH_SERVER = "https://exponea-engineering-assignment.appspot.com/api/work"


@app.route("/")
def hello():
    return redirect(url_for("smart_api_requester"))


@app.get("/api/smart")
def smart_api_requester():
    response = requests.get(BLOOMREACH_SERVER)

    if response.status_code == HTTPStatus.OK:
        return jsonify(success=True, response=response.json())
    else:
        return jsonify(success=False)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)
