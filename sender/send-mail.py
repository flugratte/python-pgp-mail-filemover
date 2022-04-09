import configparser
import os
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

        for file in os.listdir(CONSUME_DIR):
            print("Processing:", file)
            SUBJECT = "New Document " + str(datetime.now())
            FILEPATH = os.path.join(CONSUME_DIR, file)
            e = (Envelope()
                 .subject(SUBJECT)
                 .message("See attachment")
                 .from_(MAIL_FROM)
                 .to(MAIL_TO)
                 .attach(path=FILEPATH)
                 .encryption()
                 )
            e.as_message()  # returns EmailMessage
            success = e.smtp(SMTP_HOST, int(SMTP_PORT), SMTP_USER, SMTP_PASS, "tls").send()  # directly sends
            if success:
                print("Sent:", file)
                os.remove(FILEPATH)
            else:
                print("Failed to send:", file)

    if SLEEP_TIME > 0:
        time.sleep(SLEEP_TIME)
    else:
        break
