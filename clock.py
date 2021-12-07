import re
import os
from sys import stderr
from psycopg2 import connect
from contextlib import closing
from datetime import datetime
from datetime import timedelta
from sendemail import send_buyer_reservation_notification, send_seller_reservation_notification, send_buyer_reservation_reminder, send_seller_reservation_reminder, send_buyer_expiration_notification, send_seller_expiration_notification
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler({'apscheduler.timezone': 'UTC'})

def days_between(d1, d2, seller, buyer, item_name):
    d1 = datetime.strptime(str(d1), "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(str(d2), "%Y-%m-%d %H:%M:%S")
    #print("Current Date:", d1)
    #print("Reserved Date:", d2)
    time_left = timedelta(days=3) - (d1-d2)
    # print("TIME LEFTTTTTT",time_left)
    time_split = (re.split('[ :]', str(time_left)))[0]
    print(str(time_split))
    if int(time_split) < 0:
        send_buyer_expiration_notification(seller, buyer, item_name)
        send_seller_expiration_notification(seller, buyer, item_name)
        return("YOUR RESERVATION HAS EXPIRED! 0 days left")
        # send email that reservation has expired
    # print(int(time_split))
    # if time_left < 0:
    #     print("TIME LEFT IS NEGATIVE")
    #     return("TIME LEFT TO RESERVE HAS EXPIRED!")
    #print("Old time left:", (d1-d2))
    #print("Time left:", time_left)
    left = str(time_left).split(':', 1)
    time_left = left[0]
    mins_secs_left = left[1]
    print("helloooo", str(time_left))
    if "day" not in str(time_left):
        hours_left = (str(time_left).split(', ', 1))[-1] # hours left on 0th day
        print("YOUR RESERVATION IS ABOUT TO EXPIRE! Only", str(hours_left), "hours left!")
        send_buyer_reservation_reminder(seller, buyer, item_name)
        send_seller_reservation_reminder(seller, buyer, item_name)
        return("YOUR RESERVATION WILL EXPIRE IN ", str(hours_left), " HOURS!")
    #print(mins_secs_left)
    #print("Adjusted date:", time_left, " hours!")
    # I DONT THINK THIS EVER GETS HIT
    if time_left == str(0):
        mins_secs_left = mins_secs_left.replace(":", " minutes ")
        return(mins_secs_left, " seconds left")
    print("TIME LEFT:", time_left)
    print("Time Left Split:", (str(time_left).split(', ', 1))[-1])
    return(time_left, " hours left")

# @sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
@sched.scheduled_job('interval', minutes=2)
def scheduled_job():
    print('This job is run every day at 5pm.')
    DATABASE_URL = os.environ.get('DATABASE_URL')

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                stmt_str = 'SELECT * FROM reservations INNER JOIN items ON items.itemid = reservations.itemid AND items.sellernetid = reservations.sellernetid WHERE reservations.completedtime IS NULL;'
                cursor.execute(stmt_str)

                row = cursor.fetchone()

                list_of_items = []
                while row is not None:
                    item = {'itemid': row[0],
                    'buyernetid': row[1],
                    'sellernetid': row[2],
                    'reserved_time': row[3],
                    'status': row[17],
                    'prodname': row[19]}
                    list_of_items.append(item)
                    row = cursor.fetchone()

                for item in list_of_items:
                    # send buyer email
                    stmt_str = ('SELECT * from users where netid = %s')
                    cursor.execute(stmt_str, [item['buyernetid']])
                    row = cursor.fetchone()
                    buyer = {'netid': row[0],
                    'email': row[1],
                    'phone': row[3],
                    'first_name': row[4],
                    'last_name': row[5],
                    'full_name': row[6]}

                    stmt_str = ('SELECT * from users where netid = %s')
                    cursor.execute(stmt_str, [item['sellernetid']])
                    info = cursor.fetchone()
                    seller = {'netid': row[0],
                    'email': row[1],
                    'phone': row[3],
                    'first_name': row[4],
                    'last_name': row[5],
                    'full_name': row[6]}

                    if item['status'] != 1:
                        print("MISMATCH RESERVATION ITEM!!!")
                    # make sure to check in email template that if seller/buyer phone number is unknown then dont inlcude it email template
                    # get time stamp
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.utcnow()
                    dt = now.strftime(f)
                    days_between(dt, item['reserved_time'], seller, buyer, item['prodname']) # this is a string! # email should be sent in here! 
                    # reservation_time_left = ''.join(time_left_to_complete_reservation)
                    # print(str(reservation_time_left))
                    # item['reservation_time_left']: str(reservation_time_left)
                    # error if item in reservation table is not marked as reserved in items table
                    # if item['status'] == 1:
                    #     results.append(item)
                    
                    
                # print("printed curr_reserved items!!!! ")
                return True

    except Exception as ex:
       # print(ex, file=stderr)
        exit(1)



sched.start()

while True:
    pass
