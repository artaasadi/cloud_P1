import requests
import database
import rabbit_MQ

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



if __name__ == '__main__':
    rabbit_MQ.rabbitMQ_receive(callback=callback)
