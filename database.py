import os
from sys import stderr
from psycopg2 import connect
from contextlib import closing
from datetime import datetime
from datetime import timedelta

# add to users table if user is not already in the table (first time user)
def add_user(user_info):
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
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.utcnow()
                    dt = now.strftime(f)
                    #print("started inserting into users table")
                    stmt_str = ('INSERT INTO users (netid, email, joined, phone, first_name, last_name, full_name) VALUES (%s, %s, %s, %s, %s, %s, %s)')
                    cursor.execute(stmt_str, [user_info['netid'], user_info['email'], dt, user_info['phone'], user_info['first_name'], user_info['last_name'], user_info['full_name']])
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

                    stmt_str = ('SELECT first_name, email from users where netid = %s')
                    cursor.execute(stmt_str, [sellernetid])
                    row = cursor.fetchone()
                    seller_first_name = row[0]
                    seller_email = row[1]
                    print("SELLER FIRST_NAME: ", seller_first_name)
                    print("SELLER EMAIL: ", seller_email)
                    connection.commit()
    
    except Exception as ex:
       print(ex, file=stderr)
       #exit(1)

    return sellernetid, seller_first_name, seller_email
    

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
                dt = now.strftime(f)

                # add user if first time user
                # when CAS authenticates, do this, move it
                add_user(user_info)
                
                # insert item into items table
                stmt_str = ('INSERT INTO items '
                + '(type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status, sellernetid, prodname, photolink1, photolink2, photolink3) ' +
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, %s)")
                cursor.execute(stmt_str, [item['type'], item['subtype'], item['size'], item['gender'], item['price'], item['color'], item['condition'], item['brand'], item['desc'], dt, item['photolink'], user_info['netid'], item['prodname'], item['photolink1'], item['photolink2'], item['photolink3']])                # get most recent itemid inserted (item id of currently inserted item)
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

def delete_reserve(user_info, itemid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = "DELETE FROM reservations where itemid = %s"
                cursor.execute(stmt_str, [itemid])
                print("deleted from reservations")
                # row = cursor.fetchone()

                stmt_str = "UPDATE items SET status=0 WHERE itemid= %s"
                cursor.execute(stmt_str, [itemid])
                print("updated items table")
                # send email notification to seller that this person deleted their reservation

                connection.commit()

    except Exception as ex:
       print(ex, file=stderr)
       # exit(1)

def complete_reserve(user_info, itemid):
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
                dt = now.strftime(f)

                stmt_str = "UPDATE reservations SET completedtime = %s WHERE itemid = %s"
                cursor.execute(stmt_str, [dt, itemid])
                print("completed reservations from reservations")
                # row = cursor.fetchone()

                stmt_str = "UPDATE items SET status=2 WHERE itemid= %s"
                cursor.execute(stmt_str, [itemid])
                print("updated items table")
                # send email notification to seller that this person deleted their reservation

                connection.commit()

    except Exception as ex:
       print(ex, file=stderr)
       # exit(1)

def days_between(d1, d2):
    d1 = datetime.strptime(str(d1), "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(str(d2), "%Y-%m-%d %H:%M:%S")
    #print("Current Date:", d1)
    #print("Reserved Date:", d2)
    time_left = timedelta(days=5) - (d1-d2)
    #print("Old time left:", (d1-d2))
    #print("Time left:", time_left)
    left = str(time_left).split(':', 1)
    time_left = left[0]
    mins_secs_left = left[1]
    #print(mins_secs_left)
    #print("Adjusted date:", time_left, " hours!")
    if time_left == str(0):
        mins_secs_left = mins_secs_left.replace(":", " minutes ")
        return(mins_secs_left, " seconds left")
    return(time_left, " hours left")


def reserved_items(user_info):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = 'SELECT * FROM reservations WHERE completedtime IS NULL AND buyernetid = %s;'
                cursor.execute(stmt_str, [user_info['netid']])

                # connection.commit()

                row = cursor.fetchone()

                item_ids = {}
                results = []
                while row is not None:
                    itemid = row[0]
                    reserved_time = row[3]
                    item_ids[itemid] = reserved_time
                    row = cursor.fetchone()

                for item_id in item_ids:
                    stmt_str = ('SELECT * from items where itemid = %s')
                    cursor.execute(stmt_str, [item_id])
                    item_info = cursor.fetchone()
                    # get time stamp
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.utcnow()
                    dt = now.strftime(f)
                    time_left_to_complete_reservation = days_between(dt, item_ids[item_id]) # this is a string! 
                    reservation_time_left = ''.join(time_left_to_complete_reservation)
                    # print(str(reservation_time_left))
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
                    'prodname': item_info[14],
                    'reservation_time_left': str(reservation_time_left)
                    }
                    stmt_str = ('SELECT * from users where netid = %s')
                    cursor.execute(stmt_str, [item['sellernetid']])
                    seller_info = cursor.fetchone()
                    seller_full_name = seller_info[6]
                    item['seller_full_name'] = seller_full_name
                    # error if item in reservation table is not marked as reserved in items table
                    if item['status'] == 1:
                        results.append(item)
                    if item['status'] != 1:
                        print("MISMATCH RESERVATION ITEM!!!")
                    

                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)
def seller_reservations(user_info):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = 'SELECT * FROM reservations WHERE completedtime IS NULL AND sellernetid = %s;'
                cursor.execute(stmt_str, [user_info['netid']])

                # connection.commit()

                row = cursor.fetchone()

                item_ids = {}
                results = []
                while row is not None:
                    itemid = row[0]
                    reserved_time = row[3]
                    item_ids[itemid] = reserved_time
                    row = cursor.fetchone()

                # counter = 1
                for item_id in item_ids:
                    stmt_str = ('SELECT * from items where itemid = %s')
                    cursor.execute(stmt_str, [item_id])
                    item_info = cursor.fetchone()
                    # get time stamp
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.utcnow()
                    dt = now.strftime(f)
                    time_left_to_complete_reservation = days_between(dt, item_ids[item_id]) # this is a string! 
                    reservation_time_left = ''.join(time_left_to_complete_reservation)
                    stmt_str = ('SELECT buyernetid from reservations where itemid = %s')
                    cursor.execute(stmt_str, [item_id])
                    buyernetid = cursor.fetchone()[0]
                    stmt_str = ('SELECT full_name from users where netid = %s')
                    cursor.execute(stmt_str, [item['buyernetid']])
                    buyerfullname = cursor.fetchone()[0]
                    # print(str(reservation_time_left))
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
                    'prodname': item_info[14],
                    'reservation_time_left': str(reservation_time_left),
                    'buyernetid': buyernetid,
                    'buyerfullname': buyerfullname
                    }
                    
                    # error if item in reservation table is not marked as reserved in items table
                    if item['status'] == 1:
                        results.append(item)
                        counter = counter+1
                #     if counter > len(item_ids):
                #         break
                # print("EXITED LOOP!!!")
                print(results)
                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)
def past_purchases(user_info):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = 'SELECT * FROM reservations WHERE completedtime IS NOT NULL AND buyernetid = %s;'
                cursor.execute(stmt_str, [user_info['netid']])

                # connection.commit()

                row = cursor.fetchone()

                item_ids = {}
                results = []
                while row is not None:
                    itemid = row[0]
                    completed_time = row[4]
                    item_ids[itemid] = completed_time
                    row = cursor.fetchone()

                for item_id in item_ids:
                    stmt_str = ('SELECT * from items where itemid = %s')
                    cursor.execute(stmt_str, [item_id])
                    item_info = cursor.fetchone()
                    print(item_info)
                    purchased_date = datetime.strptime(str(item_ids[item_id]), "%Y-%m-%d %H:%M:%S.%f")
                    print(purchased_date)
                    purchased_date = (str(purchased_date).split(' ', 1))[0]
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
                    'prodname': item_info[14],
                    'purchase_completed': str(purchased_date)
                    }
                    # error if item in reservation table is not marked as reserved in items table
                    if item['status'] == 2:
                        results.append(item)
                    

                return results

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)

def all_brands():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    brands = []
    try:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                stmt_str = "SELECT DISTINCT brand from items"
                cursor.execute(stmt_str)
                row = cursor.fetchone()

                while row is not None:
                    brands.append(row[0])
                    row = cursor.fetchone()

    except Exception as ex:
        print(ex, file=stderr)
        return brands

    return brands

def search_items(search, filter):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    search_results = []

    try:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:
                stmt_str = "SELECT * from items "
                cmd_args = []
            
                stmt_str += "where prodname LIKE %s "

                if search is None:
                    search = ""

                cmd_args.append("%" + search + "%")

                if filter:
                    if 'type' in filter and filter['type'] is not None and filter["type"] != '':
                        print("entered type if")
                        stmt_str += "AND type = %s "
                        cmd_args.append(filter['type'])
                    if 'subtype' in filter and filter['subtype'] is not None and filter["subtype"] != '':
                        stmt_str += "AND subtype = %s "
                        cmd_args.append(filter['subtype'])
                    if 'size' in filter and filter['size'] is not None and filter["size"] != '':
                        stmt_str += "AND size = %s "
                        cmd_args.append(filter['size'])
                    if 'gender' in filter and filter['gender'] is not None and filter["gender"] != '':
                        stmt_str += "AND gender = %s "
                        cmd_args.append(filter['gender'])
                    if 'brand' in filter and filter['brand'] is not None and filter["brand"] != '':
                        stmt_str += "AND brand = %s "
                        cmd_args.append(filter['brand'])
                    if 'condition' in filter and filter['condition'] is not None and filter["condition"] != '':
                        stmt_str += "AND condition = %s "
                        cmd_args.append(filter['condition'])
                    if 'color' in filter and filter['color'] is not None and filter["color"] != '':
                        stmt_str += "AND color = %s "
                        cmd_args.append(filter['color'])
          
                # change order by when sort by is in place
                stmt_str += "ORDER BY itemid ASC"

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
        return None

    print(str(len(results)) + " items")
    return results



# delete item from shop page and respective tables (seller wants to take item off market)
# def delete_item()

    
