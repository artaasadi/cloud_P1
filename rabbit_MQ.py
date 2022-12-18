import pika
import database

AMQP_URL = "amqps://cbhdouwe:7duJD8hk6R2axZI3qdAncYXEXm6a6LPw@fuji.lmq.cloudamqp.com/cbhdouwe"
my_db = database.Db()

def rabbitMQ_receive(callback):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='advertisements')

    channel.basic_consume(queue='advertisements', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def rabbitMQ_send(id):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='advertisements')

    channel.basic_publish(exchange='', routing_key='advertisements', body=id)
    
    print(" id %r Sent to rabbitMQ queue  " % id)
    connection.close()