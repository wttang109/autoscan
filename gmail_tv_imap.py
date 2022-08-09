# -*-coding:utf-8-*-
__author__ = 'Sunny'

import imaplib
import email
import re
from datetime import datetime, timedelta
import time
import requests

fpath = '***'

def send_notice(text):
    line_url = "***"
    params = {"message": "{}".format(text)}
    r = requests.post(line_url, headers=headers, params=params)
    # print(r.status_code)  # 200

    params = {"message": "{}".format(text)}
    r2 = requests.post(line_url, headers=headers2, params=params)


def main():
    # credentials
    username = "***"

    # generated app password
    app_password = "***"

    # https://www.systoolsgroup.com/imap/
    gmail_host = 'imap.gmail.com'

    # set connection
    mail = imaplib.IMAP4_SSL(gmail_host)

    # login
    mail.login(username, app_password)

    # select inbox
    mail.select("INBOX")

    # select specific mails
    _, selected_mails = mail.search(None, '(FROM "***")')

    # total number of mails from specific user
    # print("Total Messages from noreply@tradingview.com:", len(selected_mails[0].split()))
    count = 0
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(current_time, 'Scan Loop')
    for num in reversed(selected_mails[0].split()):
        if count < 30:
            _, data = mail.fetch(num, '(RFC822)')
            _, bytes_data = data[0]

            # convert the byte data to message
            email_message = email.message_from_bytes(bytes_data)
            # email_message = email.message_from_string(bytes_data)
            print("===========================================")

            # access data
            # print("Subject: ", email_message["subject"])
            # print("To:", email_message["to"])
            # print("From: ", email_message["from"])
            # print("Date: ", email_message["date"])
            # print(re.split(r'[^\S\n\r]+', email_message["date"].strip()))

            d = re.split(r'[^\S\n\r]+', email_message["date"].strip())[1]
            m = re.split(r'[^\S\n\r]+', email_message["date"].strip())[2]
            m = month(m)
            y = re.split(r'[^\S\n\r]+', email_message["date"].strip())[3]
            t = re.split(r'[^\S\n\r]+', email_message["date"].strip())[4]
            u = re.split(r'[^\S\n\r]+', email_message["date"].strip())[5]

            date_str = '{}-{}-{} {}'.format(y, m, d, t)
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            date_utc8 = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
            print(date_utc8)

            for part in email_message.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    message = part.get_payload(decode=True)
                    
                    usdttype = re.search('Your (.*)USDT', message.decode())
                    signal = re.search(';">(.*)</p>', message.decode())
                    print(usdttype.group(1), signal.group(1), count)
                    print("==========================================\n")
                    logline = str(date_utc8) + ' ' + usdttype.group(1) + ' ' + signal.group(1) + '\n'

                    with open(fpath, 'r') as file:
                        content = file.read()
                        if logline in content:
                            file.close()
                        else:
                            send_notice(logline)
                            f = open(fpath, 'a')
                            f.write(logline)
                            f.close()
                    break
            count = count + 1
        else:
            print('Scan Completed')
            print(' ')
            print(' ')
            break
    time.sleep(10)
    #     break  #
    # break  #


if __name__ == "__main__":
    while 1:
        try:
            main()
        except Exception as e:
            print(e)
            time.sleep(5)
