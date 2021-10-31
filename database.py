import os
from psycopg2 import connect
from contextlib import closing
from datetime import datetime

def add_item(item):
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
                + '(itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status) ' +
                "VALUES (DEFAULT, %s, %s, %s, %s, %f, %s, %s, %s, %s, %s, %s, %i)")
                cursor.execute(stmt_str, [item.type, item.subtype, item.gender, item.price, item.color, item.condition, item.brand, item.desc, testDate, item.photolink, item.status])

                connection.commit()

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)

    
