import imaplib
from email import message_from_bytes
import json
import sqlite3


def main():
    username, password = get_credentials()

    verified = True
    while verified:
        emails = get_email_to_group()
        if emails == -1:
            print('Enter a valid email.')
            break
        elif emails is False:
            print('List emails in the specified format.')
            break
        conn, c = create_tables()
        group_emails(conn, c, emails, username, password)
        verified = False


def get_credentials():
    with open('config.json', 'r') as file:
        config = json.load(file)
        username = config.get('EMAIL_HOST_USER')
        password = config.get('EMAIL_HOST_PASSWORD')
    return username, password


def get_email_to_group():
    emails = []
    try:
        emails_to_group = input('Enter the email(s) you want to group: ').split(', ')
        if emails_to_group:
            for email in emails_to_group:
                if '@' in email:
                    local_part, domain_part = email.split('@')
                    if local_part and domain_part:
                        emails.append({'local_part': local_part,
                                       'domain_part': domain_part,
                                       'email': email
                                       })
                    else:
                        return -1
                else:
                    return -1
            return emails
        else:
            return -1
    except ValueError:
        return False


def create_tables():
    conn = sqlite3.connect('uid.db')
    c = conn.cursor()
    with conn:
        c.execute("""
                    CREATE TABLE IF NOT EXISTS UIDs (
                        uid integer UNIQUE NOT NULL
                    )
                  """)
    return conn, c


def get_uid(uid):
    uid_as_list = uid
    _, _, uid_as_byte = uid_as_list[0].split()
    uid = uid_as_byte[:-1]
    uid = uid.decode('utf-8')
    return uid


def create_folder(mail, email):
    if '<' in email['email'] or '>' in email['email']:
        email_name = email['domain_part'].replace('.', '_').replace('>', '_')
        folder_name = f'Emails_from_{email_name}'
        mail.create(folder_name)
        return folder_name
    else:
        folder_name = f'Emails_from_{email["local_part"]}'
        mail.create(folder_name)
        return folder_name


def copy_mails(mail, email, list_of_msg_indexes, folder_name):
    print('Copying items...')
    for num in reversed(list_of_msg_indexes):
        _, msg_in_bytes = mail.fetch(num, '(RFC822)')
        msg_in_bytes = msg_in_bytes[0][1]
        msg = message_from_bytes(msg_in_bytes)
        if msg['From'] == email["email"]:
            mail.copy(num, folder_name)
    return True


def tracker(conn, c, mail, number_of_emails, list_of_msg_indexes):
    if number_of_emails == 0:
        last_processed_email = list_of_msg_indexes[-1]
        _, uid = mail.fetch(last_processed_email, '(UID)')
        uid = get_uid(uid)
        with conn:
            c.execute("SELECT * FROM UIDs")
            all_uid = c.fetchall()
            all_uid = [str(row_uid) for row in all_uid for row_uid in row]
            if uid in all_uid:
                pass
            else:
                c.execute("INSERT INTO UIDs (uid) VALUES (:uid)", {'uid': uid})
        return True


def group_emails(conn, c, emails, username, password):
    host = 'imap.gmail.com'
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select('Inbox')

    number_of_emails = len(emails)

    for email in emails:
        folder_name = create_folder(mail, email)

        typ, msg_index_in_bytes = mail.search(None, 'ALL')
        list_of_msg_indexes = msg_index_in_bytes[0].split()

        with conn:
            c.execute("SELECT uid FROM UIDs ORDER BY rowid DESC LIMIT 1")
            last_processed_uid = c.fetchone()
            if last_processed_uid is None:
                copied = copy_mails(mail, email, list_of_msg_indexes, folder_name)
                if copied is True:
                    print(f'Messages from {email["email"]} has been copied to {folder_name} folder.')

                number_of_emails -= 1
                email_tracker = tracker(conn, c, mail, number_of_emails, list_of_msg_indexes)
                if email_tracker is True:
                    print('Tracked.')
            else:
                search_parameter = f'UID {int(last_processed_uid[0]) + 1}:*'
                _, msg_index_in_bytes = mail.search(None, search_parameter)
                list_of_msg_indexes = msg_index_in_bytes[0].split()
                copied = copy_mails(mail, email, list_of_msg_indexes, folder_name)
                if copied is True:
                    print(f'Messages from {email["email"]} has been copied to {folder_name} folder.')

                number_of_emails -= 1
                email_tracker = tracker(conn, c, mail, number_of_emails, list_of_msg_indexes)
                if email_tracker is True:
                    print('Tracked.')


if __name__ == '__main__':
    main()
