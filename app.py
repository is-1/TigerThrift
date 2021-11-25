import requests
import hashlib
import os
import json
import random
import sys
import urllib.parse
import urllib.request
from base64 import b64encode
from flask import Flask, request, make_response
from flask import render_template
from datetime import datetime
from database import add_user, add_item, all_items, reserve_item, search_items, item_details, reserved_items
from sendemail import send_buyer_notification, send_seller_notification
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

    r = requests.get(url=urllib.parse.urljoin(TIGERBOOK_API, 'katelynr'),headers=get_wsse_headers(TIGERBOOK_USR, TIGERBOOK_KEY))
    # Only do if undergrad
    if str(r) == "<Response [404]>":
        print("NOT AN UNDERGRAD!!!!")
        # return and do some error handling
        return
    phone = '512-263-6973' # THIS IS HARDCODED...NEED TO CHANGE
    user_info = {'first_name': (r.json())['first_name'],
    'last_name': (r.json())['last_name'],
    'netid': netid,
    'email': ((r.json())['email']).lower(),
    'class_year': (r.json())['class_year'],
    'phone': phone,
    'photo_link': (r.json())['photo_link']}
    return user_info

# Home page
@app.route('/', methods=['GET'])
@app.route('/buy', methods=['GET'])
def buy():
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    add_user(user_info)

    items = all_items()

    html = render_template('buy.html', items=items)

    response = make_response(html)
    return response
    
@app.route('/sell', methods=['GET', 'POST'])
def sell():
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

    # # call function
    if prodname is not None:
        item_details = {'prodname': prodname,
        'type': itemtype,
        'subtype': subtype,
        'desc': description,
        'gender': gender,
        'price': price,
        'size': size,
        'brand': brand,
        'condition': condition,
        'color': color,
        'photolink': photolink}
        add_item(item_details, user_info)
    html = render_template('sell.html')
    response = make_response(html)
    return response


@app.route('/searchresults', methods=['GET'])
def search_results():
    CasClient().authenticate()
    search = request.args.get('search')

    filter = {"none" : None} #placeholder

    if search is not None:
        print("search: "  + search)
        items = search_items(search, filter)   
        html = render_template('searchresults.html', items=items)

    response = make_response(html)

    return response

@app.route('/reserve', methods=['POST'])
def reserve():
    username = CasClient().authenticate()
    user_info = get_user_info(username)
    add_user(user_info)
    buyer = {'name': user_info['first_name'], 'netid': user_info['netid'], 'email': user_info['email']} # add full name 

    itemid = request.form.get('itemid')

    sellernetid = reserve_item(buyer['netid'], str(itemid)) # retreive seller netid
    # get seller from database eventually, USE USERS TABLE 
    seller = {'name': 'katie', 'netid': str(sellernetid), 'email':'katielchou@princeton.edu'} # get seller info (from users table)

    # change to item object, or item name based on itemid
    send_seller_notification(seller, buyer, itemid) # check this
    send_buyer_notification(buyer, itemid) # eecheck this
    
    html = render_template('success_reserve.html')
    response = make_response(html)
    return response
 

@app.route('/profile', methods=['GET'])
def profile():
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    add_user(user_info)
    
    items = all_items()
    curr_reserved_items = reserved_items(user_info)
    
    html = render_template('profile.html', user_info = user_info, items=items, curr_reserved_items=curr_reserved_items) # pass in currently reserved items

    response = make_response(html)
    return response

@app.route('/itemdetails', methods=['GET'])
def itemdetails():
    CasClient().authenticate()
    # html = render_template('itemdetails.html')
    itemid = request.args.get('itemid')

    item = item_details(itemid)
    
    print("item = " + str(item))

    html = render_template('itemdetails.html', item=item)
    response = make_response(html)
    return response

@app.route('/about', methods=['GET'])
def about():
    html = render_template('about.html')
    response = make_response(html)
    return response

@app.route('/tutorial', methods=['GET'])
def tutorial():
    html = render_template('tutorial.html')
    response = make_response(html)
    return response

@app.route('/error', methods=['GET'])
def error():
    html = render_template('error.html')
    response = make_response(html)
    return response

# log out the user
@app.route('/logout', methods=['GET'])
def logout():
    print("logging out the user!!!")
    cas_client = CasClient()
    cas_client.authenticate()
    cas_client.logout('buy')

if __name__ == "__main__":
    app.run(host='localhost')
