import os
from sys import stderr
from psycopg2 import connect
from contextlib import closing
from datetime import datetime

# add to users table if user is not already in the table (first time user)
def add_user(user_info, currDate):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                # check if user is first time user, if so add to users table
                stmt_str = 'SELECT exists (SELECT 1 FROM users WHERE netid = %s LIMIT 1);'
                cursor.execute(stmt_str, [user_info['netid']])
                row = cursor.fetchone() # returned as tuple boolean
                is_user = row[0]
                print("ARE THEY ALREADY A USER???? " + str(is_user))
                # if new user, insert into users table
                if not is_user:
                    #print("started inserting into users table")
                    stmt_str = ('INSERT INTO users (netid, email, joined, phone) VALUES (%s, %s, %s, %s)')
                    cursor.execute(stmt_str, [user_info['netid'], user_info['email'], currDate, user_info['phone']])
                    #print("finished inserting into users table")
                connection.commit()
    
    except Exception as ex:
       print(ex, file=stderr)
       exit(1)

    

# when user uploads an item, update necessary tables
def add_item(item, user_info):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                
                # get time stamp
                f = '%Y-%m-%d %H:%M:%S'
                now = datetime.utcnow()
                testDate = now.strftime(f)

                # add user if first time user
                # when CAS authenticates, do this, move it
                add_user(user_info, testDate)
                
                # insert item into items table
                stmt_str = ('INSERT INTO items '
                + '(type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status) ' +
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'google.com', 0)")
                cursor.execute(stmt_str, [item['type'], item['subtype'], item['size'], item['gender'], item['price'], item['color'], item['condition'], item['brand'], item['desc'], testDate])
                # get most recent itemid inserted (item id of currently inserted item)
                stmt_str = 'SELECT last_value FROM items_itemid_seq;'
                cursor.execute(stmt_str)
                row = cursor.fetchone()
                recent_item_id = row[0] # int data type
                print("LAST INSERTED INDEX: " + str(recent_item_id))
                # insert into sellers table 
                stmt_str = ('INSERT INTO sellers '
                + '(netid, itemid) ' +
                "VALUES (%s, %s)")
                cursor.execute(stmt_str, [user_info['netid'], str(recent_item_id)])


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
                    item = {'itemid': row[0],
                    'type': row[1],
                    'subtype': row[2],
                    'desc': row[9],
                    'gender': row[4],
                    'price': row[5],
                    'size': row[3],
                    'brand': row[8],
                    'condition': row[7],
                    'color': row[6]}
                    results.append(item)
                    row = cursor.fetchone()

                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)


# delete item from shop page and respective tables (seller wants to take item off market)
# def delete_item()

    
