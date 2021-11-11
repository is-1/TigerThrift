import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_seller_notification(seller, item): 

    message = Mail(
        from_email= 'tigerthrift@princeton.edu',
        to_emails= seller['email']
    )
        # subject='Test Notification Email',
        # html_content='<strong>you have reserved an item</strong>')

    message.dynamic_template_data = {
        'name': seller['name'],
        'prodname': item
    }

    message.template_id = 'd-34e62704618448cd970bd0d8eb96f925'


    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)