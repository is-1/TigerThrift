import requests
import hashlib
import os
import json
import random
import sys
import urllib.parse
import urllib.request
from base64 import b64encode
from flask import Flask, redirect, url_for, request, make_response
from titlecase import titlecase
from flask import render_template
from datetime import datetime
from database import add_user, add_item, reserve_item, search_items, item_details, reserved_items, seller_reservations, items_sold_in_past, past_purchases, delete_reserve, complete_reserve, all_brands, remove_item
from sendemail import send_buyer_notification, send_seller_notification, send_buyer_reminder, send_seller_reminder
from casclient import CasClient
from keys import APP_SECRET_KEY

############################################

# try:
from tigerbook_credentials import API_KEY as TIGERBOOK_KEY
from tigerbook_credentials import USERNAME as TIGERBOOK_USR
# except ImportError:
#     TIGERBOOK_USR = os.environ.get("TIGERBOOK_USR", None)
#     TIGERBOOK_KEY = os.environ.get("TIGERBOOK_KEY", None)

class TigerbookCredentialsException(Exception):
    pass

# TIGERBOOK_IMG="https://tigerbook.herokuapp.com/images/"
TIGERBOOK_API="https://tigerbook.herokuapp.com/api/v1/undergraduates/"

###########################################

app = Flask(__name__, template_folder = '.')
app.secret_key = APP_SECRET_KEY

def get_wsse_headers(username, password):
    """
    Returns the WSSE headers needed for authentication
    into the Tigerbook API / website.
    """
    if username == None or password == None:
        return {}
    
    NONCE_SIGNATURE = (
        "0123456789abcdefghijklmnopqrstuvwxyz" +
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ+/=")
    rand_chars = ''.join([random.choice(NONCE_SIGNATURE) for i in range(32)])
    nonce = b64encode(rand_chars.encode("ascii")).decode("ascii")
    created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    digest = b64encode(hashlib.sha256((nonce + created + password).encode('ascii')).digest())
    headers = {
        'Authorization': 'WSSE profile="UsernameToken"',
        'X-WSSE': ('UsernameToken Username="%s", PasswordDigest="%s", '
                   + 'Nonce="%s", Created="%s"')
                  % (username, digest.decode("ascii"), nonce, created)
    }
    return headers

# given username returned from CAS, compile netid, email, and phone number from user
def get_user_info(username):
    if '\n' in username:
        username = username.split('\n', 1)[0]

    print("USERNAME (from cas): " + username)
    netid = username

    r = requests.get(url=urllib.parse.urljoin(TIGERBOOK_API, netid),headers=get_wsse_headers(TIGERBOOK_USR, TIGERBOOK_KEY))
    # Only do if undergrad
    if str(r) == "<Response [404]>":
        print("NOT AN UNDERGRAD!!!!")
        # return and do some error handling
        return
    phone = '512-263-6973' # THIS IS HARDCODED...NEED TO CHANGE
    user_info = {'first_name': (r.json())['first_name'],
    'last_name': (r.json())['last_name'],
    'full_name': (r.json())['full_name'],
    'netid': netid,
    'email': ((r.json())['email']).lower(),
    'class_year': (r.json())['class_year'],
    'phone': phone,
    'photo_link': (r.json())['photo_link']}
    return user_info

@app.route('/login', methods=['GET'])
def login():
    print("went into login function")
    CasClient().authenticate()
    return redirect(url_for('buy')) # after authenticating, send to buy page 

@app.route('/', methods=['GET'])
@app.route('/landing', methods=['GET'])
def landing():
    if CasClient().authenticateFirst() != False:
        print("logged in")
        return redirect(url_for('buy'))
    else: 
        html = render_template('landing.html')
        response = make_response(html)
        print("returned landing page")
        return response

def is_authenticated():
    if CasClient().authenticateFirst() == False:
        # return call to landing page function
        # return landing()
        # html = render_template('landing.html')
        print("entered if statement")
        # response = make_response(html)
        # return response
        return redirect(url_for('landing'))
    else:
        print("entered true")
        return True

# Home page
@app.route('/buy', methods=['GET'])
def buy():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    add_user(user_info)
    search = request.args.get('search')

    gender = request.args.get('gender')
    size = request.args.get('size')
    brand = request.args.get('brand')
    type = request.args.get('type')
    subtype = request.args.get('subtype')
    condition = request.args.get('condition')
    color = request.args.get('color')
    sort = request.args.get('sort')

    if gender is None:
        gender = ""
    if size is None:
        size = ""
    if brand is None:
        brand = ""
    if type is None:
        type = ""
    if subtype is None:
        subtype = ""
    if condition is None:
        condition = ""
    if color is None:
        color = ""
    if sort is None:
        sort = "newest to oldest"

    # filter = {"subtype" : "sneakers"} #placeholder
    filter = {"gender": gender, "type": type, 
    "subtype": subtype, "size": size, "condition": condition,
    "color": color, "brand": brand}

    print("search: "  + str(search))
    print("filter: " + str(filter))
    print("sort: " + str(sort))

    items = search_items(search, filter, sort)

    brands = all_brands()

    html = render_template('buy.html', items=items, brands=brands, user_info=user_info, prev_search=search, prev_filter=filter, prev_sort=sort)

    response = make_response(html)
    return response
    
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    add_user(user_info)

    html = render_template('sell.html')
    response = make_response(html)
    return response

@app.route('/success_sell', methods=['GET', 'POST'])
def success_sell():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    prodname = request.form.get('prodname')
    gender = request.form.get('gender')
    price = request.form.get('price')
    size = request.form.get('size')
    brand = request.form.get('brand')
    itemtype = request.form.get('type')
    subtype = request.form.get('subtype')
    condition = request.form.get('condition')
    color = request.form.get('color')
    description = request.form.get('description')
    photolink = request.form.get('photolink')
    photolink1 = request.form.get('photolink1')
    photolink2 = request.form.get('photolink2')
    photolink3 = request.form.get('photolink3')

    # # call function
    if prodname is not None:
        item_details = {'prodname': titlecase(prodname),
        'type': titlecase(itemtype),
        'subtype': titlecase(subtype),
        'desc': description,
        'gender': titlecase(gender),
        'price': price,
        'size': titlecase(size),
        'brand': titlecase(brand),
        'condition': titlecase(condition),
        'color': titlecase(color),
        'photolink': photolink, 
        'photolink1': photolink1,
        'photolink2': photolink2,
        'photolink3': photolink3}
        add_item(item_details, user_info)
    html = render_template('success_sell.html')
    response = make_response(html)
    return response


@app.route('/searchresults', methods=['GET'])
def search_results():
    CasClient().authenticate()
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    search = request.args.get('search')

    gender = request.args.get('gender')
    size = request.args.get('size')
    brand = request.args.get('brand')
    type = request.args.get('type')
    subtype = request.args.get('subtype')
    condition = request.args.get('condition')
    color = request.args.get('color')

    sort = request.args.get('sort')

    # filter = {"subtype" : "sneakers"} #placeholder
    filter = {"gender": gender, "type": type, 
    "subtype": subtype, "size": size, "condition": condition,
    "color": color, "brand": brand}

    print("search: "  + search)
    print("filter: " + str(filter))
    print("sort: " + sort)

    items = search_items(search, filter, sort)
    html = render_template('searchresults.html', items=items, user_info=user_info)

    response = make_response(html)
    response.set_cookie('search', str(search))
    response.set_cookie('filter', json.dumps(filter))
    response.set_cookie('sort', str(sort))

    return response

@app.route('/reserve', methods=['POST'])
def reserve():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)
    buyer = {'name': user_info['first_name'], 'netid': user_info['netid'], 'email': user_info['email']} # add full name 

    itemid = request.form.get('itemid')

    sellernetid, seller_first_name, seller_email, product_name = reserve_item(buyer['netid'], str(itemid)) # retreive seller netid
    # get seller from database eventually, USE USERS TABLE 
    seller = {'name': str(seller_first_name), 'netid': str(sellernetid), 'email': str(seller_email)} # get seller info (from users table)

    # change to item object, or item name based on itemid
    send_seller_notification(seller, buyer, product_name) # check this
    send_seller_reminder(seller, buyer, product_name) # for testing
    send_buyer_notification(buyer, product_name) # eecheck this
    send_buyer_reminder(buyer, product_name) # for testing

    
    html = render_template('success_reserve.html')
    response = make_response(html)
    return response

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    itemid = request.form.get('itemid')
    print("entered delete reserve")
    delete_reserve(user_info, itemid)
    
    html = render_template('success_cancel_reservation.html')
    response = make_response(html)
    return response

@app.route('/complete_reservation', methods=['POST'])
def complete_reservation():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    itemid = request.form.get('itemid')
    complete_reserve(user_info, itemid)
    
    html = render_template('success_complete_reservation.html')
    response = make_response(html)
    return response

# this function completely removes from database (status 2 means item was already sold)
# need to handle the case where the item is reserved by someone but seller wants to delete it. ACTUALLY IT WOULDN'T EVEN BE DISPLAYED IN THAT SECTION
@app.route('/delete_item', methods=['POST'])
def delete_item():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    itemid = request.form.get('itemid')
    remove_item(itemid)
    
    html = render_template('success_item_deleted.html')
    response = make_response(html)
    return response
 

@app.route('/profile', methods=['GET'])
def profile():
    is_authenticated()
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)
    
    items = search_items(None, None, None)
    curr_reserved_items = reserved_items(user_info)
    reserved_by_others = seller_reservations(user_info)
    past_sold_items = items_sold_in_past(user_info)
    purchased_items = past_purchases(user_info)

    curr_active_items = []
    for item in items:
        if item['sellernetid'] == user_info['netid']:
            if item['status'] == 0:
                curr_active_items.append(item)
            # if item['status'] == 1:
            #     reserved_by_others_items.append(item)
    html = render_template('profile.html', user_info = user_info, items=items, curr_active_items=curr_active_items, curr_reserved_items=curr_reserved_items, reserved_by_others=reserved_by_others, purchased_items=purchased_items, past_sold_items=past_sold_items) # pass in currently reserved items

    response = make_response(html)
    return response

@app.route('/itemdetails', methods=['GET'])
def itemdetails():
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)

    itemid = request.args.get('itemid')
    search = request.cookies.get('search')
    filter = json.loads(request.cookies.get('filter'))
    sort = request.cookies.get('sort')

    item = item_details(itemid)
    
    print("item = " + str(item))
    print("previous search = " + str(search))
    print("previous filter = " + str(filter))
    print("previous type = " + filter['type'])
    print("type of filter = " + str(type(filter)))
    print("previous sort = " + str(sort))

    html = render_template('itemdetails.html', item=item, user_info = user_info, prev_search=search, prev_filter=filter, prev_sort=sort)
    response = make_response(html)
    return response

@app.route('/about', methods=['GET'])
def about():
    is_authenticated()
    html = render_template('about.html')
    response = make_response(html)
    return response

@app.route('/tutorial', methods=['GET'])
def tutorial():
    is_authenticated()
    html = render_template('tutorial.html')
    response = make_response(html)
    return response

@app.route('/error', methods=['GET'])
def error():
    html = render_template()
    response = make_response(html)
    return response

# log out the user
@app.route('/logout', methods=['GET'])
def logout():
    print("logging out the user!!!")
    cas_client = CasClient()
    cas_client.authenticate()
    cas_client.logout('landing')

if __name__ == "__main__":
    app.run(host='localhost')
