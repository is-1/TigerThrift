import os
from sys import stderr
from psycopg2 import connect
from contextlib import closing
from datetime import datetime

def add_item(item):
    print("HIIIIIII")
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                f = '%Y-%m-%d %H:%M:%S'
                now = datetime.utcnow()
                testDate = now.strftime(f)

                stmt_str = ('INSERT INTO items '
                + '(type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status) ' +
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'google.com', 0)")
                cursor.execute(stmt_str, [item['type'], item['subtype'], item['size'], item['gender'], item['price'], item['color'], item['condition'], item['brand'], item['desc'], testDate])

                connection.commit()

    except Exception as ex:
       print(ex, file=stderr)
       exit(1)

def all_items():
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = "SELECT * from items"
                cursor.execute(stmt_str)

                connection.commit()

                row = cursor.fetchone()

                results = []
                while row is not None:
                    results.append(row)
                    row = cursor.fetchone()

                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)


    
