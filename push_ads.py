import requests
import uuid
import database
import boto3
import logging
from botocore.exceptions import ClientError
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import rabbit_MQ

app = Flask(__name__)
data = SQLAlchemy(app)

my_db = database.Db()


class Ad(data.Model):
    id = data.Column(data.Integer, primary_key=True)
    email = data.Column(data.String(100), nullable=False)
    description = data.Column(data.String, nullable=False)
    image_url = data.Column(data.String, nullable=False)


def save_image(image_url, advertisement_id):
    response = requests.get(image_url)
    if response.status_code:
        file_name = str(advertisement_id) + '.jpg'
        fp = open(file_name, 'wb')
        fp.write(response.content)
        fp.close()
    return file_name


def save_to_s3(file_name):
    endpoint_url = 'https://storage.iran.liara.space'
    access_key = '89q6cfh9d7iv0hdm'
    secret_key = '1f3afb7a-2a3d-42b5-8a3d-fe6b440be05b'
    bucket_name = 'artacloudproj'
    s3_client = boto3.client(service_name='s3', endpoint_url=endpoint_url, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        response = s3_client.upload_file(file_name, bucket_name, file_name)
        print('response: '+response)
        url = endpoint_url + "/" + bucket_name + "/" + file_name
    except ClientError as e:
        logging.error(e)
        return None
    return url


@app.route('/', methods=['POST', 'GET'])
def request():
    if request.method == 'POST':
        advertisement = Ad(email= request.form["email"], description= request.form["description"], image_url= request.form["image"])

        advertisement.id = my_db.add_ad(advertisement.email, advertisement.description, advertisement.image_url,
                                                '', 'Checking state')

        file_name = save_image(advertisement.image_url, advertisement.id)
        url = save_to_s3(file_name)
        rabbit_MQ.rabbitMQ_send(str(advertisement.id))
        return 'your advertisement has been registered with the id %r' % advertisement.id

    if request.method == 'GET':
        advertisement_id = request.form["id"]
        data = my_db.get_by_id(advertisement_id)
        print(data[0])
        if data[0][5] == 'Checking state':
            return 'Pending...'
        elif data[0][5] == 'rejected':
            return 'Rejected!'
        else:
            return 'Accepted, the category is %s.' % data[0][4]




def create_unique_id():
    return uuid.uuid4().int


if __name__ == '__main__':
    app.run(debug=True)