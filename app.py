from flask import Flask, request, make_response
from flask import render_template
from database import add_item, all_items, reserve_item
from sendemail import send_buyer_notification, send_seller_notification

app = Flask(__name__, template_folder = '.')

@app.route('/', methods=['GET'])
@app.route('/buy', methods=['GET'])
def buy():
    items = all_items()

    html = render_template('buy.html', items=items)

    response = make_response(html)
    return response
    
@app.route('/sell', methods=['GET', 'POST'])
def index():
    # NEED TO ALSO GET USER INFO
    netid = 'katelynr' # change to request.args
    email = 'katelynr@princeton.edu'
    phone = '512-263-6973'

    prodName = request.form.get('prodName')
    gender = request.form.get('gender')
    price = request.form.get('price')
    size = request.form.get('size')
    brand = request.form.get('brand')
    itemtype = request.form.get('type')
    subtype = request.form.get('subtype')
    condition = request.form.get('condition')
    color = request.form.get('color')
    photolink = request.form.get('photolink')

    # # call function
    if prodName is not None:
        item_details = {'type': itemtype,
        'subtype': subtype,
        'desc': prodName,
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

@app.route('/reserve', methods=['POST'])
def reserve():
   
    buyer = {'name': 'katie', 'netid': 'kc42', 'email':'katielchou@princeton.edu'} # get buyer from cookies eventually

    itemid = request.form.get('itemid')

    sellernetid = reserve_item(buyer['netid'], str(itemid))

    seller = {'name': 'katie', 'netid': str(sellernetid), 'email':'katielchou@princeton.edu'} # get seller from database eventually

    send_seller_notification(seller, itemid) # change to item object, or item name based on itemid
    send_buyer_notification(buyer, itemid)
    
    return make_response("success")
 

@app.route('/profile', methods=['GET'])
def profile():
    items = all_items()
    
    html = render_template('profile.html', items=items)

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
    html = render_template('itemdetails.html')
    response = make_response(html)
    return response

if __name__ == "__main__":
    app.run()
