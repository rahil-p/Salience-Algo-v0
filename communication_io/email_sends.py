import config

import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

ADDRESS = 'sentience@rahilpatel.io'

def read_template(file):
    with open(file, 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()
    return Template(template_content)

def smtp():
    s = smtplib.SMTP(host='smtp-relay.gmail.com', port='587')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(ADDRESS, config.sentience_pass)
    return s

def pre_send(to_email, requests_array):
    s = smtp()

    template = read_template('communication_io/pre_send.txt')
    requests_text_array = ["<li>{0} <a href='{3}'>{1}</a>, "
                           "<i>capped at ${2:.2f}</i></li>".format('stock' if a.type == 'stocks' else 'crypto',
                                                                   a.symbol,
                                                                   a.cap,
                                                                   a.pre_plot) for a in requests_array]
    requests_text = '\n'.join(requests_text_array)
    message = template.substitute(DATE=str(datetime.now().date()), REQUESTS=requests_text)

    msg = MIMEMultipart()
    msg['From'] = ADDRESS
    msg['To'] = to_email
    msg['Subject'] = 'Sentience - Trading Confirmation (' + str(datetime.now().date()) + ')'
    msg.attach(MIMEText(message, 'html'))

    s.send_message(msg)
    del msg
    s.quit()

    return True

def post_send(to_email, requests_array):
    s = smtp()

    template = read_template('communication_io/post_send.txt')
    message = template.substitute()

    msg = MIMEMultipart()
    msg['From'] = ADDRESS
    msg['To'] = to_email
    msg['Subject'] = 'Sentience - Day End Summary (' + str(datetime.now().date()) + ')'
    msg.attach(MIMEText(message, 'plain'))

    s.send_message(msg)
    del msg
    s.quit()

    return True
