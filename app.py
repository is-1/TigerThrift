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
from database import add_user, get_whitelist_user_info, get_user_phone, add_user_phone, add_item, edit_item_db, reserve_item, search_items, item_details, reserved_items, seller_reservations, items_sold_in_past, past_purchases, get_seller_and_item_info, delete_reserve, complete_reserve, all_brands, remove_item, curr_active_items, reserved_netid, edit_phone
from sendemail import send_buyer_reservation_notification, send_seller_reservation_notification, send_seller_cancellation, send_buyer_cancellation
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

@app.before_request
def enforceHttpsInHeroku():
    # always force redirect to HTTPS (secure connection)
    if request.headers.get("X-Forwarded-Proto") == "http":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

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

    # whitelisting instructors who are not undergrads (prof. dondero and TAs)
    if netid in ['rdondero', 'bb5943', 'jg41', 'anatk', 'dorothyz']:
        # don't need to add_user bc we added them to database already
        user_info = get_whitelist_user_info(netid)
        return user_info

    # get info and make sure user is an undergrad
    r = requests.get(url=urllib.parse.urljoin(TIGERBOOK_API, netid),headers=get_wsse_headers(TIGERBOOK_USR, TIGERBOOK_KEY))
    # Only do if undergrad
    if str(r) == "<Response [404]>":
        print("NOT AN UNDERGRAD!!!!")
        # return and do some error handling
        return
    user_info = {'first_name': (r.json())['first_name'],
    'last_name': (r.json())['last_name'],
    'full_name': (r.json())['full_name'],
    'netid': netid,
    'email': ((r.json())['email']).lower(),
    'class_year': (r.json())['class_year'],
    'photo_link': (r.json())['photo_link']}
    add_user(user_info)
    user_info['phone'] = get_user_phone(netid)
    print("user's currently logged phone number!!! ", user_info['phone'])
    return user_info

@app.route('/login', methods=['GET'])
def login():
    print("went into login function")
    CasClient().authenticate()
    return redirect(url_for('shop')) # after authenticating, send to shop page 

@app.route('/', methods=['GET'])
@app.route('/landing', methods=['GET'])
def landing():
    if CasClient().authenticateFirst() != False:
        print("logged in")
        return redirect(url_for('shop'))
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
@app.route('/shop', methods=['GET'])
def shop():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    search = request.args.get('search')

    gender = request.args.get('gender')
    size = request.args.get('size')
    brand = request.args.get('brand')
    type = request.args.get('type')
    subtype = request.args.get('subtype')
    condition = request.args.get('condition')
    color = request.args.get('color')
    sort = request.args.get('sort')

    if search is None:
        search = ""
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
    filter = {"gender": titlecase(gender), "type": titlecase(type), 
    "subtype": titlecase(subtype), "size": size.upper(), "condition": titlecase(condition),
    "color": titlecase(color), "brand": titlecase(brand)}

    print("search: "  + str(search))
    print("filter: " + str(filter))
    print("sort: " + str(sort))

    items = search_items(search, filter, sort)
    if items is None:
        items = []

    brands = all_brands()
    if brands is None:
        brands = []

    html = render_template('shop.html', items=items, brands=brands, user_info=user_info, prev_search=search, prev_filter=filter, prev_sort=sort)

    response = make_response(html)
    response.set_cookie('search', str(search))
    response.set_cookie('filter', json.dumps(filter))
    response.set_cookie('sort', str(sort))
    response.set_cookie('route', "/shop")
    return response
    
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)
    if user_info is None:
        print("can't get user_info for netid: " + str(username))

    html = render_template('sell.html', user_info=user_info)
    response = make_response(html)
    response.set_cookie('route', "/sell")

    return response

@app.route('/edit_item', methods=['POST'])
def edit_item():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)
    itemid = request.form.get('itemid')
    route = request.cookies.get('route')

    ## item = item_details(itemid)
    item = item_details(itemid)
    item['price'] = item['price'][1:]
    
    print("route on edit page; " + str(route))
    print("item info sent to be edited:", str(item))
    html = render_template('edit.html', item=item, user_info=user_info, route=route)
    response = make_response(html)
    return response

@app.route('/success_edit', methods=['POST'])
def success_edit():
    print("entered success edit function")
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    itemid = request.form.get('itemid')
    prodname = request.form.get('prodname')
    gender = request.form.get('gender')
    price = request.form.get('price')
    priceflexibility = request.form.get('priceflexibility')
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
    user_phone = request.form.get('phone')
    print("user phone from edit-form", user_phone)
    print(itemid)
    print(prodname)
    print(gender)
    print(price)
    print(priceflexibility)

    # # call function
    if prodname is not None:
        print("entered prodname if stmt")
        item_details = {'itemid': itemid,
        'prodname': prodname,
        'type': titlecase(itemtype),
        'subtype': titlecase(subtype),
        'desc': description,
        'gender': titlecase(gender),
        'price': price,
        'priceflexibility': titlecase(priceflexibility),
        'size': size.upper(),
        'brand': titlecase(brand),
        'condition': titlecase(condition),
        'color': titlecase(color),
        'photolink': photolink, 
        'photolink1': photolink1,
        'photolink2': photolink2,
        'photolink3': photolink3}
        if str(user_phone) != "":
            print("went into if stmt")
            add_user_phone(netid=user_info['netid'], phone_number=user_phone)
        edit_item_success = edit_item_db(item_details, user_info)
        
        if not edit_item_success:
            html = render_template('error.html', message="Couldn't save edits. Please try again or contact us if the error persists.") # type this now!!! 
            print("item edit unsuccessful: itemid" + str(itemid))
            response = make_response(html)
            return response

        html = render_template('success_edit.html', item_name=item_details['prodname']) # type this now!!! 
        print("item was successfully edited!!!")
        response = make_response(html)
        return response

@app.route('/success_sell', methods=['GET', 'POST'])
def success_sell():
    is_authenticated()
    username = CasClient().authenticate()
    # username='katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    prodname = request.form.get('prodname')
    gender = request.form.get('gender')
    price = request.form.get('price')
    priceflexibility = request.form.get('priceflexibility')
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
    user_phone = request.form.get('phone')
    print("user phone from sell-form", user_phone)
    print(prodname)

    # # call function
    if prodname is not None:
        item_details = {'prodname': prodname,
        'type': titlecase(itemtype),
        'subtype': titlecase(subtype),
        'desc': description,
        'gender': titlecase(gender),
        'price': price,
        'priceflexibility': titlecase(priceflexibility),
        'size': size.upper(),
        'brand': titlecase(brand),
        'condition': titlecase(condition),
        'color': titlecase(color),
        'photolink': photolink, 
        'photolink1': photolink1,
        'photolink2': photolink2,
        'photolink3': photolink3}
        if str(user_phone) != "":
            add_user_phone(netid=user_info['netid'], phone_number=user_phone)
        add_item(item_details, user_info)
        html = render_template('success_sell.html')
        response = make_response(html)
        response.set_cookie('route', "/sell")
        return response


@app.route('/searchresults', methods=['GET'])
def search_results():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

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
    filter = {"gender": titlecase(gender), "type": titlecase(type), 
    "subtype": titlecase(subtype), "size": size.upper(), "condition": titlecase(condition),
    "color": titlecase(color), "brand": titlecase(brand)}

    print("search: "  + search)
    print("filter: " + str(filter))
    print("sort: " + sort)

    items = search_items(search, filter, sort)
    html = render_template('searchresults.html', items=items, user_info=user_info)

    response = make_response(html)
    response.set_cookie('search', str(search))
    response.set_cookie('filter', json.dumps(filter))
    response.set_cookie('sort', str(sort))
    response.set_cookie('route', "/shop")
    return response

@app.route('/reserve', methods=['POST'])
def reserve():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)
    buyer = {'first_name': user_info['first_name'], 'netid': user_info['netid'], 'email': user_info['email'], 'full_name': user_info['full_name']} # add full name 

    itemid = request.form.get('itemid')

    sellernetid, seller_first_name, seller_full_name, seller_email, product_name = reserve_item(buyer['netid'], str(itemid)) # retreive seller netid
    
    # get seller from database eventually, USE USERS TABLE 

    if sellernetid is None:
        html = render_template('error.html')
        response = make_response(html)
        return response

    seller = {'first_name': str(seller_first_name), 'full_name': str(seller_full_name), 'email': str(seller_email)} # get seller info (from users table)

    # change to item object, or item name based on itemid
    success_send = send_seller_reservation_notification(seller, buyer, product_name) # check this
    # send_seller_reservation_notification(seller, buyer, product_name) # for testing
    # send_buyer_reservation_notification(seller, buyer, product_name) # eecheck this

    # try again if failed
    if success_send == False:
        success_send = send_seller_reservation_notification(seller, buyer, product_name)
        if success_send == False:
            print("error, tried twice seller notification not sent for itemid " + str(itemid))
            html = render_template('error.html', itemid=itemid)
            response = make_response(html)
            return response

    success_send = send_buyer_reservation_notification(seller, buyer, product_name) # for testing
    if success_send == False:
        success_send = send_buyer_reservation_notification(seller, buyer, product_name)
        if success_send == False:
            print("error, tried twice buyer notification not sent for itemid " + str(itemid))
            html = render_template('error.html', itemid=itemid)
            response = make_response(html)
            return response

    html = render_template('success_reserve.html', itemid=itemid)
    response = make_response(html)
    return response

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    is_authenticated()
    username = CasClient().authenticate()
    # username='katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)
    buyer = {'first_name': user_info['first_name'], 'full_name': user_info['full_name'], 'email': user_info['email']}
    itemid = request.form.get('itemid')
    seller, item_name = get_seller_and_item_info(itemid)
    delete_reserve(user_info, itemid)
    print("successfully deleted item from db")
    # send cancellation email confirmation to buyer and seller, make sure to include correct parameters
    send_seller_cancellation(seller, buyer, str(item_name))
    send_buyer_cancellation(seller, buyer, str(item_name))
    
    html = render_template('success_cancel_reservation.html')
    response = make_response(html)
    return response

@app.route('/complete_reservation', methods=['POST'])
def complete_reservation():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    itemid = request.form.get('itemid')
    buyernetid, buyer_full_name = reserved_netid(itemid)
    complete_reserve(user_info, itemid)
    
    html = render_template('success_complete_reservation.html', buyer_full_name=buyer_full_name)
    response = make_response(html)
    return response

# this function completely removes from database (status 2 means item was already sold)
# need to handle the case where the item is reserved by someone but seller wants to delete it. ACTUALLY IT WOULDN'T EVEN BE DISPLAYED IN THAT SECTION
@app.route('/delete_item', methods=['POST'])
def delete_item():
    is_authenticated()
    username = CasClient().authenticate()
    # username='katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    itemid = request.form.get('itemid')
    remove_item(itemid)
    
    html = render_template('success_item_deleted.html')
    response = make_response(html)

    return response
 

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    
    phone = request.form.get('phone')
    print("phone: " + str(phone))
    print("username: " + str(phone))

    if phone is not None:
        edit_success = edit_phone(username, phone)
        if not edit_success:
            html = render_template('error.html')
            response = make_response(html)
            return response

    user_info = get_user_info(username)

    active_items = curr_active_items(user_info)
    # print(active_items)
    curr_reserved_items = reserved_items(user_info)
    # print(curr_reserved_items)
    reserved_by_others = seller_reservations(user_info)
    # print(reserved_by_others)
    past_sold_items = items_sold_in_past(user_info)
    print("PAST SOLD ITEMS")
    print(past_sold_items)
    purchased_items = past_purchases(user_info)
    print("PURCHASED ITEMS")
    print(purchased_items)

    if active_items is None:
        active_items = []

    html = render_template('profile.html', user_info = user_info, curr_active_items=active_items, curr_reserved_items=curr_reserved_items, reserved_by_others=reserved_by_others, purchased_items=purchased_items, past_sold_items=past_sold_items) # pass in currently reserved items

    response = make_response(html)
    response.set_cookie('route', "/profile")

    return response


@app.route('/edit_profile', methods=['GET'])
def edit_profile():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)
    
    active_items = curr_active_items(user_info)
    # print(active_items)
    curr_reserved_items = reserved_items(user_info)
    # print(curr_reserved_items)
    reserved_by_others = seller_reservations(user_info)
    # print(reserved_by_others)
    past_sold_items = items_sold_in_past(user_info)
    print("PAST SOLD ITEMS")
    print(past_sold_items)
    purchased_items = past_purchases(user_info)
    print("PURCHASED ITEMS")
    print(purchased_items)

    if active_items is None:
        active_items = []

    html = render_template('profile.html', user_info = user_info, curr_active_items=active_items, curr_reserved_items=curr_reserved_items, reserved_by_others=reserved_by_others, purchased_items=purchased_items, past_sold_items=past_sold_items) # pass in currently reserved items

    response = make_response(html)
    response.set_cookie('route', "/profile")

    return response


@app.route('/mypurchased', methods=['GET'])
def my_purchased():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    purchased_items = past_purchases(user_info)

    if purchased_items is None:
        purchased_items = []
        
    html = render_template('mypurchased.html', user_info = user_info, purchased_items=purchased_items)

    response = make_response(html)
    response.set_cookie('route', "/mypurchased")

    return response

@app.route('/myreserved', methods=['GET'])
def my_reserved():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    curr_reserved_items = reserved_items(user_info)

    if curr_reserved_items is None:
        curr_reserved_items = []
        
    html = render_template('myreserved.html', user_info = user_info, curr_reserved_items=curr_reserved_items)
    response = make_response(html)
    response.set_cookie('route', "/myreserved")

    return response

#@app.route('/myselling', methods=['GET'])
#def my_selling():
#    is_authenticated()
#    username = CasClient().authenticate()
#    #username = 'katelynr'
#    user_info = get_user_info(username)
    # add_user(user_info)

#    active_items = curr_active_items(user_info)

#    if active_items is None:
#        active_items = []
        
#    html = render_template('myselling.html', user_info = user_info, curr_active_items=active_items)

#    response = make_response(html)
#    response.set_cookie('route', "/myselling")

#    return response

@app.route('/myselling/active', methods=['GET'])
def my_selling_active():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    active_items = curr_active_items(user_info)

    if active_items is None:
        active_items = []
        
    html = render_template('mysellingactive.html', user_info = user_info, curr_active_items=active_items, status="active")

    response = make_response(html)
    response.set_cookie('route', "/myselling/active")

    return response

@app.route('/myselling', methods=['GET'])
@app.route('/myselling/reserved', methods=['GET'])
def my_selling_reserved():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    # active_items = curr_active_items(user_info)
    reserved_by_others = seller_reservations(user_info)

    if reserved_by_others is None:
        reserved_by_others = []
        
    html = render_template('mysellingreserved.html', user_info = user_info, reserved_by_others=reserved_by_others, status="reserved")

    response = make_response(html)
    response.set_cookie('route', "/myselling/reserved")

    return response

@app.route('/mysold', methods=['GET'])
def my_sold():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    past_sold_items = items_sold_in_past(user_info)

    if past_sold_items is None:
        past_sold_items = []
        
    html = render_template('mysold.html', user_info = user_info, past_sold_items=past_sold_items)

    response = make_response(html)
    response.set_cookie('route', "/mysold")
    return response

@app.route('/itemdetails', methods=['GET'])
def itemdetails():
    is_authenticated()
    username = CasClient().authenticate()
    # username = 'katelynr'
    user_info = get_user_info(username)
    # add_user(user_info)

    itemid = request.args.get('itemid')
    search = request.cookies.get('search')
    filter = json.loads(request.cookies.get('filter'))
    sort = request.cookies.get('sort')
    route = request.cookies.get('route')
    print("request: " + str(request))

    item = item_details(itemid)

    if item is None:
        html = render_template('error.html', message="This item may not exist or you don't have access to it. Contact us if this is a mistake.")
        response = make_response(html)
        response.set_cookie('route', "/shop")
        return response

    print("itemid = " + str(itemid))
    buyernetid, buyer_full_name = reserved_netid(itemid)
    
    if buyernetid is not None and user_info['netid'] == buyernetid:
        isMine = True
    elif buyernetid is not None and item['status'] != 2 and user_info['netid'] != buyernetid and item['sellernetid'] != user_info['netid']:
        html = render_template('error.html', message="This item may not exist or you don't have access to it. Contact us if this is a mistake.")
        response = make_response(html)
        response.set_cookie('route', "/shop")
        return response
    else:
        isMine = False

    print("route = " + str(route))
    print("item = " + str(item))
    print("previous search = " + str(search))
    print("previous filter = " + str(filter))
    print("previous type = " + filter['type'])
    print("type of filter = " + str(type(filter)))
    print("previous sort = " + str(sort))
    # print("photolink1 = " + str(item['photolink1']))
    # print("photolink2 = " + str(item['photolink2']))
    print("isMine = " + str(isMine))
    print("reserved by = " + str(buyernetid))

    html = render_template('itemdetails.html', item=item, user_info = user_info, prev_search=search, prev_filter=filter, prev_sort=sort, route=route, isMine=isMine)
    response = make_response(html)
    response.set_cookie('route', "/itemdetails")
    return response

@app.route('/about', methods=['GET'])
def about():
    # if not logged in
    if CasClient().authenticateFirst() == False:
        print("not logged in")
        html = render_template('about.html', logged_in=False)
        response = make_response(html)
    # if logged in
    else:
        print("logged in")
        html = render_template('about.html', logged_in=True)
        response = make_response(html)
    
    response.set_cookie('route', "/about")
    return response

@app.route('/tutorial', methods=['GET'])
def tutorial():
    # if not logged in
    if CasClient().authenticateFirst() == False:
        print("not logged in")
        html = render_template('tutorial.html', logged_in=False)
        response = make_response(html)
    # if logged in
    else:
        print("logged in")
        html = render_template('tutorial.html', logged_in=True)
        response = make_response(html)
    
    response.set_cookie('route', "/tutorial")
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
