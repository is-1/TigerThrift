#!/usr/bin/env python

#-----------------------------------------------------------------------
# create.py
# Author: Katie Chou, Iroha Shirai, Katelyn Rodrigues
#-----------------------------------------------------------------------
import os
from sys import argv, stderr, exit
from contextlib import closing
from psycopg2 import connect 
from datetime import datetime
# IMPORT DATE DATA TYPE

#-----------------------------------------------------------------------

def main():

    if len(argv) != 1:
        print('Usage: python create.py', file=stderr)
        exit(1)

    DATABASE_URL = os.environ['DATABASE_URL']

    try:
       # with connect(
            #host='localhost', port=5432, user='rmd', password='TigerThrift',
            #database='tigerthrift') as connection:
        with connect (DATABASE_URL, sslmode='require') as connection:
            with closing(connection.cursor()) as cursor:

                #------------------------------------------------------- create items table
                cursor.execute("DROP TABLE IF EXISTS items")

                f = '%Y-%m-%d %H:%M:%S'
                now = datetime.utcnow()
                testDate = now.strftime(f)
                cursor.execute('CREATE TABLE items ("itemid" int NOT NULL, type text, subtype text, size ' + 
                'varchar(10), gender varchar(10), price money, color text, condition text, brand text, "desc" text,' + 
                'posted timestamp, photolink text, status int)')
                # INSERT TEST DATA!!!
                stmt_str = ("INSERT INTO items "
                     + '(itemid, type, subtype, size, gender, price, condition, brand, "desc", posted, photolink, status) '
                     + "VALUES (0, 't-shirt', 'crop', 'XS', 'F', 10.50, 'like new',  'topshop', 'never worn', %s, null, 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)

                stmt_str = ('INSERT INTO items '
                + '(itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status) ' +
                "VALUES (1, 'bottom', 'skirt', 'M', 'F', 10, 'white', 'brand new', 'Urban Outfitters', 'white pleated skirt', %s, 'https://www.google.com/', 1)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)

                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' + 
                "VALUES (2, 'top', 'shirt', 'M', 'F', 10, 'white', 'gently used', 'Zara', 'white satin blouse', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)

                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' + 
                "VALUES (3, 'top', 'blouse', 'M', 'F', 10, 'white', 'very used', 'Uniqlo', 'white turtleneck', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status) ' + 
                "VALUES (4, 'top', 'tank', 'S', 'F', 8, 'white', 'gently used', 'Aritzia', 'white cropped ribbed tank', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (5, 'top', 'bodysuit', 'M', 'F', 20, 'black', 'fairly used', 'Aritzia', 'black square neck bodysuit', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])


                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (6, 'top', 'bodysuit', 'M', 'F', 20, 'black', 'brand new', 'Aritzia', 'black square neck bodysuit', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (7, 'top', 'sweater', 'one-size', 'F', 12, 'blue', 'gently used', 'Brandy Melville', 'blue white sweater vest', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (8, 'outerwear', 'jacket', 'L', 'F', 12, 'black', 'like new', 'Zara', 'leather jacket', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (9, 'outerwear', 'coat', 'S (W)', 'F', 12, 'black', 'gently used', 'Nordstrom', 'black wrap coat', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow()
                testDate = now.strftime(f)
                stmt_str = ('INSERT INTO items (itemid, type, subtype, size, gender, price, color, condition, brand, "desc", posted, photolink, status)' +
                "VALUES (10, 'shoes', 'heels/dress shoes', '8.5', 'F', 12, 'black', 'very used', 'Kate Spade', 'wrap heels', %s, 'https://www.google.com/', 0)")
                cursor.execute(stmt_str, [testDate])


            
                #------------------------------------------------------- create users table

                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("CREATE TABLE users "
                    + '("netid" text, email text, joined timestamp, phone text)')

                now = datetime.utcnow()
                testDate = now.strftime(f)

                stmt_str = ("INSERT INTO users (netid, email, joined, phone) VALUES ('ishirai', 'ishirai@princeton.edu', %s, '6033066672')")
                cursor.execute(stmt_str, [testDate])

                now = datetime.utcnow() 
                testDate = now.strftime(f)
                stmt_str = ("INSERT INTO users (netid, email, joined, phone) VALUES ('kc42', 'kc42@princeton.edu', %s, '6503916837')")
                cursor.execute(stmt_str, [testDate])

                #------------------------------------------------------- create sellers table 

                cursor.execute("DROP TABLE IF EXISTS sellers")
                cursor.execute("CREATE TABLE sellers "
                    + '("netid" text, "itemid" text)')
                cursor.execute("INSERT INTO sellers "
                     + "(netid, itemid) VALUES "
                     + "('ishirai',0)")
             

                #------------------------------------------------------- create reservations table

                cursor.execute("DROP TABLE IF EXISTS reservations")
                cursor.execute("CREATE TABLE reservations "
                    + '("itemid" text, "buyernetid" text, "sellernetid" text, "reservedtime" timestamp, "completedtime" timestamp)')
                # cursor.execute("INSERT INTO zipcodes "
                #     + "(zipcode, city, state) "
                #     + "VALUES ('08540','Princeton', 'NJ')")
                # cursor.execute("INSERT INTO zipcodes "
                #     + "(zipcode, city, state) "
                #     + "VALUES ('02138','Cambridge', 'MA')")
                # cursor.execute("INSERT INTO zipcodes "
                #     + "(zipcode, city, state) "
                #     + "VALUES ('02142','Cambridge', 'MA')")

                #-------------------------------------------------------

                connection.commit()

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()

