import requests
import uuid
import database
import boto3
import logging
from botocore.exceptions import ClientError
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
data = SQLAlchemy(app)

my_db = database.Db()


class ad(data.Model):
    id = data.Column(data.Integer, primary_key=True)
    email = data.Column(data.String(100), nullable=False)
    description = data.Column(data.String, nullable=False)
    image_url = data.Column(data.String, nullable=False)


@app.route('/', methods=['POST', 'GET'])
def request():
    pass