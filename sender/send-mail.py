import configparser
import os
import smtplib
import time
from datetime import datetime

import gnupg
from envelope import Envelope

CERTS_DIR = "/certs/"
CONSUME_DIR = "/consume/"

config = configparser.RawConfigParser()
config.read(r'config.ini')

SLEEP_TIME = int(os.environ.get("SLEEP_TIME", config.get("Sleep", "time")))

if os.listdir(CERTS_DIR):
    gpg = gnupg.GPG()
    for key in os.listdir(CERTS_DIR):
        gpg.import_keys(open(os.path.join(CERTS_DIR, key)).read())

while True:
    if not os.listdir(CONSUME_DIR):
        print(datetime.now(), "| Nothing to do")
    else:
        print(datetime.now(), "| New document(s)")
        MAIL_FROM = os.environ.get("MAIL_FROM", config.get("Mail", "from"))
        MAIL_TO = os.environ.get("MAIL_TO", config.get("Mail", "to"))

        SMTP_HOST = os.environ.get("SMTP_HOST", config.get("SMTP", "host"))
        SMTP_PORT = os.environ.get("SMTP_PORT", config.get("SMTP", "port"))
        SMTP_USER = os.environ.get("SMTP_USER", config.get("SMTP", "user"))
        SMTP_PASS = os.environ.get("SMTP_PASS", config.get("SMTP", "pass"))

        smtp_connection = smtplib.SMTP_SSL(host=SMTP_HOST, port=int(SMTP_PORT))
        smtp_connection.login(SMTP_USER, SMTP_PASS)
        print(datetime.now(), "| SMTP Connection ready")
        for file in os.listdir(CONSUME_DIR):
            print(datetime.now(), "Processing:", file)
            SUBJECT = "New Document " + str(datetime.now())
            FILEPATH = os.path.join(CONSUME_DIR, file)
            e = (Envelope()
                 .smtp(smtp_connection, int(SMTP_PORT), SMTP_USER, SMTP_PASS, "tls")
                 .subject(SUBJECT)
                 .message("See attachment")
                 .from_(MAIL_FROM)
                 .to(MAIL_TO)
                 .attach(path=FILEPATH)
                 .encryption()
                 )
            e.as_message()  # returns EmailMessage
            success = e.send()  # directly sends
            if success:
                print(datetime.now(), "Sent:", file)
                os.remove(FILEPATH)
            else:
                print(datetime.now(), "Failed to send:", file)
        smtp_connection.close()

    if SLEEP_TIME > 0:
        time.sleep(SLEEP_TIME)
    else:
        break
