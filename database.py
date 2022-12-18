import os
import psycopg2

class Db:
    '''initiate the database configuration'''
    def __init__(self):
        self.conn = psycopg2.connect(
            host="esme.iran.liara.ir",
            port=33846,
            database="relaxed_proskuriakova",
            user='root',
            password='pB7kP1kf0jDiLHwGtGDtBJrA')

    def add_ad(self, email, description, url, category, state):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO ads (email, description, url, cateory, state) VALUES (%s, %s, %s, %s, %s)',
                    (email, description, url, category, state))
        self.conn.commit()

    