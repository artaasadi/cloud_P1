import os
import psycopg2

class Db:
    '''initiate the database configuration'''
    def __init__(self):
        self.conn = psycopg2.connect(
            host="esme.iran.liara.ir",
            port=32504,
            database="postgres",
            user='root',
            password='wqWrIObDDeyFMCmLzjGndDuD')

    def add_ad(self, email, description, url, category, state):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO ads (email, description, url, category, state) VALUES (%s, %s, %s, %s, %s);',
                    (email, description, url, category, state))
        self.conn.commit()

    def update_category(self, category, id):
        cur = self.conn.cursor()
        cur.execute('UPDATE ads SET category = %s WHERE id = %s;', (category, id))
        self.conn.commit()

    def update_state(self, state, id):
        cur = self.conn.cursor()
        cur.execute('UPDATE ads SET state = %s WHERE id = %s;', (state, id))
        self.conn.commit()

    def get_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM ads WHERE id = %s;', (id, ))
        return cur.fetchall()