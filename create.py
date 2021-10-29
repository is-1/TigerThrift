#!/usr/bin/env python

#-----------------------------------------------------------------------
# create.py
# Author: Katie Chou, Iroha Shirai, Katelyn Rodrigues
#-----------------------------------------------------------------------

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

    try:
        with connect(
            host='localhost', port=5432, user='rmd', password='TigerThrift',
            database='tigerthrift') as connection:

            with closing(connection.cursor()) as cursor:

                #------------------------------------------------------- create items table
                f = '%Y-%m-%d %H:%M:%S'
                now = datetime.utcnow()
                testDate = now.strftime(f)
                cursor.execute("DROP TABLE IF EXISTS items")
                cursor.execute('CREATE TABLE items ("itemid" int NOT NULL, type text, subtype text, size ' + 
                'varchar(10), gender varchar(10), price money, condition text, brand text, "desc" text,' + 
                'posted timestamp, photolink text, status int)')
                # INSERT TEST DATA!!!
                stmt_str = ("INSERT INTO items "
                     + '(itemid, type, subtype, size, gender, price, condition, brand, "desc", posted, photolink, status) '
                     + "VALUES (0, 't-shirt', 'crop', 'XS', 'F', 10.50, 'new',  'topshop', 'never worn', %s, null, 0)")
                cursor.execute(stmt_str, [testDate])
                #     + "'The Practice of Programming',500)")
                # cursor.execute("INSERT INTO books "
                #     + "(isbn, title, quantity) "
                #     + "VALUES ('234',"
                #     + "'The C Programming Language',800)")
                # cursor.execute("INSERT INTO books "
                #     + "(isbn, title, quantity) "
                #     + "VALUES ('345',"
                #     + "'Algorithms in C',650)")

                #------------------------------------------------------- create users table

                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("CREATE TABLE users "
                    + '("netid" text, email text, joined timestamp, phone text)')
                # cursor.execute("INSERT INTO authors (isbn, author) "
                #     + "VALUES ('123','Kernighan')")
                # cursor.execute("INSERT INTO authors (isbn, author) "
                #     + "VALUES ('123','Pike')")
                # cursor.execute("INSERT INTO authors (isbn, author) "
                #     + "VALUES ('234','Kernighan')")
                # cursor.execute("INSERT INTO authors (isbn, author) "
                #     + "VALUES ('234','Ritchie')")
                # cursor.execute("INSERT INTO authors (isbn, author) "
                #     + "VALUES ('345','Sedgewick')")

                #------------------------------------------------------- create sellers table 

                cursor.execute("DROP TABLE IF EXISTS sellers")
                cursor.execute("CREATE TABLE sellers "
                    + '("netid" text, "itemid" text)')
                cursor.execute("INSERT INTO sellers "
                     + "(netid, itemid) VALUES "
                     + "('ishirai',0)")
                # cursor.execute("INSERT INTO customers "
                #     + "(custid, custname, street, zipcode) VALUES "
                #     + "('222','Harvard','1256 Mass Ave','02138')")
                # cursor.execute("INSERT INTO customers "
                #     + "(custid, custname, street, zipcode) VALUES "
                #     + "('333','MIT','292 Main St','02142')")

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

