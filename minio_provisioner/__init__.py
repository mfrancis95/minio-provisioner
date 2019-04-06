from flask import Flask, jsonify
from .minio import create_instance, get_instances

app = Flask(__name__)

@app.route('/create/<username>/<name>/<s3_access_key>/<s3_secret_key>')
def create(username, name, s3_access_key, s3_secret_key):
    create_instance(username, name, s3_access_key, s3_secret_key)
    return ''

@app.route('/get/<username>')
def index(username):
    return jsonify(get_instances(username))