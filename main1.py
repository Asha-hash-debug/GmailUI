import os.path
import re
import time
# import dateutil.parser as parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
# import email
from bs4 import BeautifulSoup
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def ecms():
    list = ["Pod1ecms_token.json", "Pod2ecms_token.json", "Pod3ecms_token.json", "Pod4ecms_token.json",
            "Pod5ecms_token.json", "Pod6ecms_token.json", "ecmspod7_token.json", "Pod8ecms_token.json"]
    otplist = {}

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    for mail in list:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(mail):
            creds = Credentials.from_authorized_user_file(mail, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if mail == "Pod1ecms_token.json":
                    credfile = "Pod1ecms.json"
                elif mail == "Pod2ecms_token.json":
                    credfile = "Pod2ecms.json"
                elif mail == "Pod3ecms_token.json":
                    credfile = "Pod3ecms.json"
                elif mail == "Pod4ecms_token.json":
                    credfile = "Pod4ecms.json"
                elif mail == "Pod5ecms_token.json":
                    credfile = "Pod5ecms.json"
                elif mail == "Pod6ecms_token.json":
                    credfile = "Pod6ecms.json"
                elif mail == "ecmspod7_token.json":
                    credfile = "Pod7ecms.json"
                else:
                    credfile = "Pod8ecms.json"

                flow = InstalledAppFlow.from_client_secrets_file(
                    credfile, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(mail, 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)

            if mail == "Pod1ecms_token.json":
                userId = 'pod1ecms@gmail.com'
            elif mail == "Pod2ecms_token.json":
                userId = 'pod2ecms@gmail.com'
            elif mail == "Pod3ecms_token.json":
                userId = 'pod3ecms@gmail.com'
            elif mail == "Pod4ecms_token.json":
                userId = 'pod4ecms@gmail.com'
            elif mail == "Pod5ecms_token.json":
                userId = 'pod5ecms@gmail.com'
            elif mail == "Pod6ecms_token.json":
                userId = 'pod6ecms@gmail.com'
            elif mail == "ecmspod7_token.json":
                userId = 'ecmspod7@gmail.com'
            else:
                userId = 'pod8ecms@gmail.com'

            current_time = datetime.datetime.now()  # use datetime.datetime.utcnow() for UTC time
            ten_minutes_ago = current_time - datetime.timedelta(minutes=3)
            ten_minutes_ago_epoch_ts = int(ten_minutes_ago.timestamp())  # in

            result = service.users().messages().list(userId=userId, labelIds=["INBOX"],
                                                     maxResults=2,
                                                     q=f'from:<noreply@meraki.com> after:{ten_minutes_ago_epoch_ts}').execute()
            print(result)
            # We can also pass maxResults to get any number of emails. Like this:
            # result = service.users().messages().list(maxResults=200, userId='me').execute()
            messages = result.get('messages')

            # messages is a list of dictionaries where each dictionary contains a message id.
            if messages == None:
                otplist.update({f'{mail[0:-11]}@gmail.com': None})
            else:
                # iterate through all the messages
                msgcount = 0
                for mssg in messages:
                    temp_dict = {}
                    m_id = mssg['id']  # get id of individual message
                    message = service.users().messages().get(userId='me',
                                                             id=m_id).execute()  # fetch the message using API
                    payld = message['payload']  # get payload of the message
                    headr = payld['headers']  # get header of the payload

                    for one in headr:  # getting the Subject
                        if one['name'] == 'Subject':
                            msg_subject = one['value']
                            temp_dict['Subject'] = msg_subject
                        else:
                            pass

                    for three in headr:  # getting the Sender
                        if three['name'] == 'From':
                            msg_from = three['value']
                            temp_dict['Sender'] = msg_from
                        else:
                            pass
                    temp_dict['Snippet'] = message['snippet']  # fetching message snippet

                    try:

                        # Fetching message body
                        mssg_parts = payld['parts']  # fetching the message parts
                        part_one = mssg_parts[0]  # fetching first element of the part
                        part_body = part_one['body']  # fetching body of the message
                        part_data = part_body['data']  # fetching data from the body
                        clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
                        clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
                        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
                        soup = BeautifulSoup(clean_two, "lxml")
                        mssg_body = soup.body()
                        # mssg_body is a readible form of message body
                        # depending on the end user's requirements, it can be further cleaned
                        # using regex, beautiful soup, or any other method
                        temp_dict['Message_body'] = mssg_body



                    except:
                        pass

                    # if temp_dict['Subject'] != "Your Cisco Meraki Dashboard security code" and result['resultSizeEstimate']==1:
                    #     otplist.update({f'{mail[0:-11]}@gmail.com': None})

                    if temp_dict['Subject'] == "Your Cisco Meraki Dashboard security code":
                        msgcount += 1
                        num = re.findall(r'[0-9]\d+', temp_dict["Snippet"])
                        for no in num:
                            if len(no) == 6:
                                print(no)
                                if msgcount == 1:
                                    otplist.update({f'{mail[0:-11]}@gmail.com': no})



        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    print(otplist)
    return render_template('index.html', header="ECMS DASHBOARD OTP's", result=otplist)


@app.route("/custom", methods=["GET", "POST"])
def meraki():
    list = ["Pod1meraki_token.json", "Pod2meraki_token.json", "Pod3meraki_token.json", "Pod4meraki_token.json",
            "Pod5meraki_token.json", "Pod6meraki_token.json", "Pod7meraki_token.json", "Pod8meraki_token.json",
            "Pod9meraki_token.json", "Pod10meraki_token.json", "Pod11meraki_token.json", "Pod12meraki_token.json",
            "Pod13meraki_token.json", "Pod14meraki_token.json", "Pod15meraki_token.json", "Pod16meraki_token.json",
            "Pod17meraki_token.json","Pod18meraki_token.json", "Pod19meraki_token.json", "Pod20meraki_token.json", "Pod21meraki_token.json", ]
    otplist = {}

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    for mail in list:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(mail):
            creds = Credentials.from_authorized_user_file(mail, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if mail == "Pod1meraki_token.json":
                    credfile = "Pod1meraki.json"
                elif mail == "Pod2meraki_token.json":
                    credfile = "Pod2meraki.json"
                elif mail == "Pod3meraki_token.json":
                    credfile = "Pod3meraki.json"
                elif mail == "Pod4meraki_token.json":
                    credfile = "Pod4meraki.json"
                elif mail == "Pod5meraki_token.json":
                    credfile = "Pod5meraki.json"
                elif mail == "Pod6meraki_token.json":
                    credfile = "Pod6meraki.json"
                elif mail == "Pod7meraki_token.json":
                    credfile = "Pod7meraki.json"
                elif mail == "Pod8meraki_token.json":
                    credfile = "Pod8meraki.json"
                elif mail == "Pod9meraki_token.json":
                    credfile = "Pod9meraki.json"
                elif mail == "Pod10meraki_token.json":
                    credfile = "Pod10meraki.json"
                elif mail == "Pod11meraki_token.json":
                    credfile = "Pod11meraki.json"
                elif mail == "Pod12meraki_token.json":
                    credfile = "Pod12meraki.json"
                elif mail == "Pod13meraki_token.json":
                    credfile = "Pod13meraki.json"
                elif mail == "Pod14meraki_token.json":
                    credfile = "Pod14meraki.json"
                elif mail == "Pod15meraki_token.json":
                    credfile = "Pod15meraki.json"
                elif mail == "Pod16meraki_token.json":
                    credfile = "Pod16meraki.json"
                elif mail == "Pod17meraki_token.json":
                    credfile = "Pod17meraki.json"
                elif mail == "Pod18meraki_token.json":
                    credfile = "Pod18meraki.json"
                elif mail == "Pod19meraki_token.json":
                    credfile = "Pod19meraki.json"
                elif mail == "Pod20meraki_token.json":
                    credfile = "Pod20meraki.json"
                else:
                    credfile = "Pod21meraki.json"

                flow = InstalledAppFlow.from_client_secrets_file(
                    credfile, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(mail, 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)

            if mail == "Pod1meraki_token.json":
                userId = 'pod1meraki@gmail.com'
            elif mail == "Pod2meraki_token.json":
                userId = 'pod2meraki@gmail.com'
            elif mail == "Pod3meraki_token.json":
                userId = 'pod3meraki@gmail.com'
            elif mail == "Pod4meraki_token.json":
                userId = 'pod4meraki@gmail.com'
            elif mail == "Pod5meraki_token.json":
                userId = 'pod5meraki@gmail.com'
            elif mail == "Pod6meraki_token.json":
                userId = 'pod6meraki@gmail.com'
            elif mail == "Pod7meraki_token.json":
                userId = 'pod7meraki@gmail.com'
            elif mail == "Pod8meraki_token.json":
                userId = 'pod8meraki@gmail.com'
            elif mail == "Pod9meraki_token.json":
                userId = 'pod9meraki@gmail.com'
            elif mail == "Pod10meraki_token.json":
                userId = 'pod10meraki@gmail.com'
            elif mail == "Pod11meraki_token.json":
                userId = 'pod11meraki@gmail.com'
            elif mail == "Pod12meraki_token.json":
                userId = 'pod12meraki@gmail.com'
            elif mail == "Pod13meraki_token.json":
                userId = 'pod13meraki@gmail.com'
            elif mail == "Pod14meraki_token.json":
                userId = 'pod14meraki@gmail.com'
            elif mail == "Pod15meraki_token.json":
                userId = 'pod15meraki@gmail.com'
            elif mail == "Pod16meraki_token.json":
                userId = 'pod16meraki@gmail.com'
            elif mail == "Pod17meraki_token.json":
                userId = 'pod17meraki@gmail.com'
            elif mail == "Pod18meraki_token.json":
                userId = 'pod18meraki@gmail.com'
            elif mail == "Pod19meraki_token.json":
                userId = 'pod19meraki@gmail.com'
            elif mail == "Pod20meraki_token.json":
                userId = 'pod20meraki@gmail.com'
            else:
                userId = 'pod21meraki@gmail.com'

            current_time = datetime.datetime.now()  # use datetime.datetime.utcnow() for UTC time
            ten_minutes_ago = current_time - datetime.timedelta(minutes=3)
            ten_minutes_ago_epoch_ts = int(ten_minutes_ago.timestamp())  # in

            result = service.users().messages().list(userId=userId, labelIds=["INBOX"],
                                                     maxResults=2,
                                                     q=f'from:<noreply@meraki.com> after:{ten_minutes_ago_epoch_ts}').execute()
            print(result)
            # We can also pass maxResults to get any number of emails. Like this:
            # result = service.users().messages().list(maxResults=200, userId='me').execute()
            messages = result.get('messages')

            # messages is a list of dictionaries where each dictionary contains a message id.
            if messages == None:
                otplist.update({f'{mail[0:-11]}@gmail.com': None})
            else:
                # iterate through all the messages
                msgcount = 0
                for mssg in messages:
                    temp_dict = {}
                    m_id = mssg['id']  # get id of individual message
                    message = service.users().messages().get(userId='me',
                                                             id=m_id).execute()  # fetch the message using API
                    payld = message['payload']  # get payload of the message
                    headr = payld['headers']  # get header of the payload

                    for one in headr:  # getting the Subject
                        if one['name'] == 'Subject':
                            msg_subject = one['value']
                            temp_dict['Subject'] = msg_subject
                        else:
                            pass

                    for three in headr:  # getting the Sender
                        if three['name'] == 'From':
                            msg_from = three['value']
                            temp_dict['Sender'] = msg_from
                        else:
                            pass
                    temp_dict['Snippet'] = message['snippet']  # fetching message snippet

                    try:

                        # Fetching message body
                        mssg_parts = payld['parts']  # fetching the message parts
                        part_one = mssg_parts[0]  # fetching first element of the part
                        part_body = part_one['body']  # fetching body of the message
                        part_data = part_body['data']  # fetching data from the body
                        clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
                        clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
                        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
                        soup = BeautifulSoup(clean_two, "lxml")
                        mssg_body = soup.body()
                        # mssg_body is a readible form of message body
                        # depending on the end user's requirements, it can be further cleaned
                        # using regex, beautiful soup, or any other method
                        temp_dict['Message_body'] = mssg_body



                    except:
                        pass

                    # if temp_dict['Subject'] != "Your Cisco Meraki Dashboard security code" and result['resultSizeEstimate']==1:
                    #     otplist.update({f'{mail[0:-11]}@gmail.com': None})

                    if temp_dict['Subject'] == "Your Cisco Meraki Dashboard security code":
                        msgcount += 1
                        num = re.findall(r'[0-9]\d+', temp_dict["Snippet"])
                        for no in num:
                            if len(no) == 6:
                                print(no)
                                if msgcount == 1:
                                    otplist.update({f'{mail[0:-11]}@gmail.com': no})



        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    print(otplist)
    return render_template('index.html', header="MERAKI DASHBOARD OTP's", result=otplist)


if __name__ == '__main__':
    app.run(debug=True)
