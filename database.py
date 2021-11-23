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
       #exit(1)

# create reservation

def reserve_item(buyernetid, itemid):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    try:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.utcnow()
                    dt = now.strftime(f)

                    stmt_str = ('SELECT sellernetid from items where itemid = %s')
                    cursor.execute(stmt_str, [itemid])
                    sellernetid = cursor.fetchone()[0]
                    
                    if sellernetid is None:
                        raise Exception("cannot find sellerid")
                        
                    # insert into reservations table
                    stmt_str = ('INSERT INTO reservations (itemid, buyernetid, sellernetid, reservedtime) VALUES (%s, %s, %s, %s)')
                    cursor.execute(stmt_str, [itemid, buyernetid, sellernetid, dt])

                    # change status in items table
                    stmt_str = ('SELECT status from items where itemid = %s')
                    cursor.execute(stmt_str, [itemid])
                    currentstatus = cursor.fetchone()[0]
                    if currentstatus == 1:
                        raise Exception("item already reserved")
                    if currentstatus != 0:
                        raise Exception("item unavailable for reservation")

                    stmt_str = ('UPDATE items set status = 1 where itemid = %s')
                    cursor.execute(stmt_str, [itemid])

                    print("reservation complete")
                    connection.commit()
    
    except Exception as ex:
       print(ex, file=stderr)
       #exit(1)

    return sellernetid
    

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
                + '(type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status, sellernetid, prodname) ' +
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s)")
                cursor.execute(stmt_str, [item['type'], item['subtype'], item['size'], item['gender'], item['price'], item['color'], item['condition'], item['brand'], item['desc'], testDate, item['photolink'], user_info['netid'], item['prodname']])
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
       #exit(1)

def all_items():
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = "SELECT * from items ORDER BY itemid asc"
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
                    'color': row[6],
                    'timestamp': row[10],
                    'photolink': row[11],
                    'status': row[12],
                    'sellernetid': row[13],
                    'prodname': row[14]
                    }
                    results.append(item)
                    row = cursor.fetchone()

                return results

    except Exception as ex:
       print(ex, file=stderr)
        # exit(1)

def item_details(itemid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = "SELECT * from items where itemid = %s"
                cursor.execute(stmt_str, [itemid])

                connection.commit()

                row = cursor.fetchone()

                item = {'itemid': row[0],
                    'type': row[1],
                    'subtype': row[2],
                    'desc': row[9],
                    'gender': row[4],
                    'price': row[5],
                    'size': row[3],
                    'brand': row[8],
                    'condition': row[7],
                    'color': row[6],
                    'timestamp': row[10],
                    'photolink': row[11],
                    'status': row[12],
                    'sellernetid': row[13],
                    'prodname': row[14]
                    }

                return item

    except Exception as ex:
       print(ex, file=stderr)
       # exit(1)

def reserved_items(user_info):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = 'SELECT * FROM reservations WHERE buyernetid = %s'
                cursor.execute(stmt_str, [user_info['netid']])

                # connection.commit()

                row = cursor.fetchone()

                item_ids = []
                results = []
                while row is not None:
                    itemid = row[0]
                    item_ids.append(itemid)
                    row = cursor.fetchone()

                for item_id in item_ids:
                    stmt_str = ('SELECT * from items where itemid = %s')
                    cursor.execute(stmt_str, [item_id])
                    item_info = cursor.fetchone()
                    item = {'itemid': item_info[0],
                    'type': item_info[1],
                    'subtype': item_info[2],
                    'desc': item_info[9],
                    'gender': item_info[4],
                    'price': item_info[5],
                    'size': item_info[3],
                    'brand': item_info[8],
                    'condition': item_info[7],
                    'color': item_info[6],
                    'timestamp': item_info[10],
                    'photolink': item_info[11],
                    'status': item_info[12],
                    'sellernetid': item_info[13],
                    'prodname': item_info[14]
                    }
                    # error if item in reservation table is not marked as reserved in items table
                    if item['status'] != 1:
                        print("MISMATCH RESERVATION ITEM!!!")
                    results.append(item)

                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)


def search_items(search, filter):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    search_results = []

    try:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                stmt_str = "SELECT * from items "
                cmd_args = []
                if search:
                    stmt_str += "where prodname LIKE %s"
                    cmd_args.append("%" + search + "%")
                    # unconment when filter dict is in place
                    # if filter['type']:
                    #     stmt_str += "AND type = ? "
                    #     cmd_args.append("%" + filter['type'] + "%")
                    # if filter['subtype']:
                    #     stmt_str += "AND subtype = ? "
                    #     cmd_args.append("%" + filter['subtype'] + "%")
                    # if filter['size']:
                    #     stmt_str += "AND size = ? "
                    #     cmd_args.append("%" + filter['size'] + "%")
                    # if filter['gender']:
                    #     stmt_str += "AND size = ? "
                    #     cmd_args.append("%" + filter['gender'] + "%")
                    # if filter['brand']:
                    #     stmt_str += "AND brand = ? "
                    #     cmd_args.append("%" + filter['brand'] + "%")
                    # if filter['condition']:
                    #     stmt_str += "AND condition = ? "
                    #     cmd_args.append("%" + filter['condition'] + "%")
                    # if filter['color']:
                    #     stmt_str += "AND color = ? "
                    #     cmd_args.append("%" + filter['color'] + "%")
                    

                    # if cmd_args:
                    #     stmt_str += "ESCAPE '\\' "

                    # change order by when sort by is in place
                    stmt_str += "ORDER BY itemid asc ASC"

                cursor.execute(stmt_str, cmd_args)

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
                    'color': row[6],
                    'timestamp': row[10],
                    'photolink': row[11],
                    'status': row[12],
                    'sellernetid': row[13],
                    'prodname': row[14]
                    }
                    results.append(item)
                    row = cursor.fetchone()

    except Exception as ex:
        print(ex, file=stderr)
        #exit(1)                                                                                                  
        return None

    print(str(len(results)) + " items")
    return results



# delete item from shop page and respective tables (seller wants to take item off market)
# def delete_item()

    
