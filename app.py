from flask import Flask, request, make_response
from flask import render_template
from database import add_item, all_items, reserve_item, search_items, item_details, reserved_items
from sendemail import send_buyer_notification, send_seller_notification
from casclient import CasClient
from keys import APP_SECRET_KEY

app = Flask(__name__, template_folder = '.')
app.secret_key = APP_SECRET_KEY

# Home page
@app.route('/', methods=['GET'])
@app.route('/buy', methods=['GET'])
def buy():
    username = CasClient().authenticate()
    # print("USERNAME (from cas): " + username)
    items = all_items()

    html = render_template('buy.html', items=items)

    response = make_response(html)
    return response
    
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    username = CasClient().authenticate()
    
    # NEED TO ALSO GET USER INFO
    netid = username
    email = username + '@princeton.edu'
    phone = '512-263-6973'

    # netid = 'katelynr'
    # email = 'katelynr@princeton.edu'
    # phone = '512-263-6973'

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
        user_info = {'netid': netid,
        'email': email,
        'phone': phone}
        add_item(item_details, user_info)
    # output = exec_sql_queries(dept, num, area, title)
    # # make sure of error page
    # if output == "ERROR":
    #     html = render_template('error.html')
    #     response = make_response(html)
    #     return response
    html = render_template('sell.html')
                        #    output = output,
                        #    dept = dept,
                        #    num = num,
                        #    area = area,
                        #    title = title,
                        #    prev_dept = dept,
                        #    prev_num = num,
                        #    prev_area = area,
                        #    prev_title = title)

    response = make_response(html)
    # response.set_cookie('prev_dept', dept)
    # response.set_cookie('prev_num', num)
    # response.set_cookie('prev_area', area)
    # response.set_cookie('prev_title', title)
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
    netid = "kc42"
    email = netid + "@princeton.edu"
    buyer = {'name': 'katie', 'netid': netid, 'email': email} # get buyer from cookies eventually

    itemid = request.form.get('itemid')

    sellernetid = reserve_item(buyer['netid'], str(itemid))

    seller = {'name': 'katie', 'netid': str(sellernetid), 'email':'katielchou@princeton.edu'} # get seller from database eventually

    send_seller_notification(seller, buyer, itemid) # change to item object, or item name based on itemid
    send_buyer_notification(buyer, itemid)
    
    return make_response("success")
 

@app.route('/profile', methods=['GET'])
def profile():
    username = CasClient().authenticate()

    # netid = "kc42" # change to username from CasClient().authenticate (current logged in user)
    # email = netid + "@princeton.edu"
    # phone = '512-263-6973'

    netid = username
    email = username + '@princeton.edu'
    phone = '512-263-6973'

    user_info = {'netid': netid,
        'email': email,
        'phone': phone}
    
    items = all_items()
    curr_reserved_items = reserved_items(user_info)
    
    html = render_template('profile.html', user_info = user_info, items=items, curr_reserved_items=curr_reserved_items) # pass in currently reserved items

    response = make_response(html)
    return response

#     cls_id = request.args.get('cls_id')
#     if cls_id == "":
#         html = render_template('error_missing_cls_id.html')
#         response = make_response(html)
#         return response
#     try:
#         cls_id = int(cls_id)
#     except Exception:
#         html = render_template('error_not_int.html')
#         response = make_response(html)
#         return response
#     cls_id = str(cls_id)
#     prev_dept = request.cookies.get('prev_dept')
#     prev_num = request.cookies.get('prev_num')
#     prev_area = request.cookies.get('prev_area')
#     prev_title = request.cookies.get('prev_title')
#     output = sql_details(cls_id)
#     # make sure of error page
#     if output == "ERROR":
#         html = render_template('error.html')
#         response = make_response(html)
#         return response
#     if output == "NO CLASS ID!!":
#         html = render_template('error_cls_id.html',
#                                cls_id = cls_id)
#         response = make_response(html)
#         return response
#     html = render_template('regdetails.html',
#                            output = output,
#                            cls_id = cls_id,
#                            p_dept = prev_dept,
#                            p_num = prev_num,
#                            p_area = prev_area,
#                            p_tit = prev_title)
#     response = make_response(html)
#     return response

# @app.route('/error', methods=['GET'])
# def error():
#     html = render_template('error.html')
#     response = make_response(html)
#     return response

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
    app.run()
