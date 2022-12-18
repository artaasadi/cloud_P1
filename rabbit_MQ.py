import pika
import database

AMQP_URL = "amqps://pxrjhmgr:FUMnQkHqsRKTdKc0f1Uq6H_-9zKMjjYU@possum.lmq.cloudamqp.com/pxrjhmgr"
my_db = database.Db()

def rabbitMQ_receive(callback):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='advertisements')

    channel.basic_consume(queue='advertisements', on_message_callback=callback, auto_ack=True)

    print('Pending')
    channel.start_consuming()


def rabbitMQ_send(id):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='advertisements')

    channel.basic_publish(exchange='', routing_key='advertisements', body=id)
    
    print("Added to queue :" + id)
    connection.close()