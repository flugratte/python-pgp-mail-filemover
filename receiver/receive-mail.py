import configparser
import email
import imaplib
import os
import time

import gnupg
from envelope import Envelope

config = configparser.RawConfigParser()
config.read(r'config.ini')

SLEEP_TIME = int(os.environ.get("SLEEP_TIME", config.get("Sleep", "time")))

IMAP_HOST = os.environ.get("IMAP_HOST", config.get("IMAP", "host"))
IMAP_USE_SSL = bool(os.environ.get("IMAP_USE_SSL", config.get("IMAP", "use_ssl")))
IMAP_USER = os.environ.get("IMAP_USER", config.get("IMAP", "user"))
IMAP_PASS = os.environ.get("IMAP_PASS", config.get("IMAP", "pass"))
print("Host: ", IMAP_HOST, "|", "Use SSL:", IMAP_USE_SSL, "|", "User:", IMAP_USER)

CERTS_DIR = "/certs/"
OUTPUT_DIR = "/attachments"

if os.listdir(CERTS_DIR):
    gpg = gnupg.GPG()
    for key in os.listdir(CERTS_DIR):
        gpg.import_keys(open(os.path.join(CERTS_DIR, key)).read())

while True:
    if IMAP_USE_SSL:
        imap = imaplib.IMAP4_SSL(IMAP_HOST)
    else:
        imap = imaplib.IMAP4(IMAP_HOST)
    imap.login(IMAP_USER, IMAP_PASS)

    status, messages = imap.select("INBOX")

    messages = int(messages[0])

    for i in range(messages, 0, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])

                mail = Envelope().load(msg)
                print("Subject:", mail.subject())
                print("From:", mail.from_())
                # print(mail.text())
                attachments = mail.attachments()
                for attachment in attachments:
                    # print("Attachment:", attachment.name)
                    filepath = os.path.join(OUTPUT_DIR, attachment.name)
                    # download attachment and save it
                    open(filepath, "wb").write(attachment.data)

                print("=" * 100)
        # mark mail for deletion
        imap.store(str(i), "+FLAGS", "\\DELETED")

    # permanently remove mails that are marked as deleted
    # from the selected mailbox (in this case, INBOX)
    imap.expunge()
    # close the connection and logout
    imap.close()
    imap.logout()

    time.sleep(SLEEP_TIME)
