from flask import Flask, request, make_response
from flask import render_template
from database import add_item, all_items

app = Flask(__name__, template_folder = '.')

@app.route('/', methods=['GET'])
@app.route('/sell', methods=['GET'])
def index():
    prodName = request.args.get('prodName')
    gender = request.args.get('gender')
    price = request.args.get('price')
    size = request.args.get('size')
    brand = request.args.get('brand')
    itemtype = request.args.get('itemtype')
    subtype = request.args.get('subtype')
    condition = request.args.get('condition')
    color = request.args.get('color')
    photolink = request.args.get('upPhoto')

    # num = request.args.get('num', default="")
    # area = request.args.get('area', default="")
    # title = request.args.get('title',default="")
    # prev_dept = request.cookies.get('prev_dept')
    # if prev_dept is None:
    #     prev_dept = '(None)'
    # prev_num = request.cookies.get('prev_num')
    # if prev_num is None:
    #     prev_num = '(None)'
    # prev_area = request.cookies.get('prev_area')
    # if prev_area is None:
    #     prev_area = '(None)'
    # prev_title = request.cookies.get('prev_title')
    # if prev_title is None:
    #     prev_title = '(None)'

    # # call function
    if prodName is not None:
        print("YO")
        item_details = {'type': itemtype,
        'subtype': subtype,
        'desc': prodName,
        'gender': gender,
        'price': price,
        'size': size,
        'brand': brand,
        'condition': condition,
        'color': color}
        add_item(item_details)
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

# @app.route('/regdetails', methods=['GET'])
# def regdetails():
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

if __name__ == "__main__":
    app.run()
