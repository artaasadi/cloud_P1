import requests
import database
import rabbit_MQ
import pika

AMQP_URL = "amqps://pxrjhmgr:FUMnQkHqsRKTdKc0f1Uq6H_-9zKMjjYU@possum.lmq.cloudamqp.com/pxrjhmgr"

my_db = database.Db()


def image_tagging(image_url):
    api_key = 'acc_f64a584bf693383'
    api_secret = 'a698123e2cba84a522a56d42182051b7'
    response = requests.get(
        'https://api.imagga.com/v2/tags?image_url=%s' % image_url,
        auth=(api_key, api_secret))
    tags = response.json().get('result').get('tags')
    most_confidence_tag = tags[0]['tag']['en']
    for tag in tags:
        confidence = tag.get('confidence')
        tag_name = tag['tag']['en']
        if tag_name == 'vehicle':
            if confidence >= 50:
                return most_confidence_tag
    return False


def send_message(email, subject, text):
    return requests.post(
        f"https://api.mailgun.net/v3/sandbox7149c4028e444207ad88cf84f5d71abc.mailgun.org/messages",
        auth=("api", "9dcb91bf4d2298623aca891edd592dee-2de3d545-ca972ffc"),
        data={"from": "<mailgun@sandbox7149c4028e444207ad88cf84f5d71abc.mailgun.org>",
              "to": [email],
              "subject": subject,
              "text": text})

    
def callback(ch, method, properties, body):
        print(body)
        id = body.decode("utf-8")
        data = my_db.get_by_id(id)[0]
        email = data[1]
        url = data[3]
        result = image_tagging(url)

        if result is True:
            category = data[4]
            my_db.update_state(id, "accepted")
            my_db.update_category(id, result)
            message = "advertisement accepted with the category of " + category
            print(message)
            send_message(email, "advertising request", message)
        else:
            my_db.update_state(id, 'rejected')
            message = "advertisement rejected"
            print(message)
            send_message(email, 'advertising request', message)


def main_receive():
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='advertisements')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        id = body.decode("utf-8")
        ad_email = database.select_data(id)[0][1]
        ad_image_url = database.select_data(id)[0][3]
        result = image_tagging(ad_image_url)

        if result is not False:
            print("yes")
            database.update_data_category(id, result)
            database.update_data_state(id, 'accepted')
            ad_category = database.select_data(id)[0][4]
            send_message(ad_email, 'advertising request',
                                'advertisement accepted with the category of %s' % ad_category)
        else:
            print("no")
            database.update_data_state(id, 'rejected')
            send_message(ad_email, 'advertising request', 'advertisement rejected')
        # cur = database.conn.cursor()
        # cur.execute('SELECT * FROM test;')
        # adds = cur.fetchall()
        # print(adds)

    channel.basic_consume(queue='advertisements', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    #rabbit_MQ.rabbitMQ_receive(callback=callback)
    main_receive()