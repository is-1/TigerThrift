import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From

# send seller notification when their item has been reserved
def send_seller_reservation_notification(seller, buyer, item_name): 

    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= seller['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'seller': seller['first_name'],
        'buyer': buyer['full_name'],
        'Weblink': buyer['email'],
        'prodname': item_name
    }

    message.template_id = 'd-34e62704618448cd970bd0d8eb96f925'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))


def send_buyer_reservation_notification(seller, buyer, item_name): 

    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= buyer['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'buyer': buyer['first_name'],
        'prodname': item_name,
        'seller_full_name': seller['full_name'],
        'seller_email': seller['email']
    }

    message.template_id = 'd-2ecc34fa76b540a8b41152f925dfcd01'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))

def send_buyer_reservation_reminder(seller, buyer, item_name):
    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= buyer['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'buyer': buyer['first_name'],
        'prodname': item_name,
        'seller': seller['full_name'],
        'Weblink': seller['email']
    }

    message.template_id = 'd-52bcd2394cbb4f63a70bc6e7c2c50645'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        print(str(e))

def send_seller_reservation_reminder(seller, buyer, item_name):
    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= seller['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'seller': seller['first_name'],
        'buyer': buyer['full_name'],
        'Weblink': buyer['email'],
        'prodname': item_name
    }

    message.template_id = 'd-08ff0c1398894d1bbbcb8e850a7e8080'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        print(str(e))

def send_buyer_expiration_notification(seller, buyer, item_name):
    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= buyer['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'buyer': buyer['first_name'],
        'prodname': item_name,
        'seller': seller['full_name'],
        'Weblink': seller['email']
    }

    message.template_id = 'd-875e76a6e7b542d5a578750cb44ab2a4'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        print(str(e))

def send_seller_expiration_notification(seller, buyer, item_name):
    message = Mail(
        from_email= From('tigerthrift@princeton.edu', 'TigerThrift'),
        to_emails= seller['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'seller': seller['first_name'],
        'buyer': buyer['full_name'],
        'Weblink': buyer['email'],
        'prodname': item_name
    }

    message.template_id = 'd-9647730514d94655bb99a0c408a989b4'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        print(str(e))