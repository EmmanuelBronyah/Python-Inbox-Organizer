import imaplib
import socket
import sqlite3
import getpass
from email import message_from_bytes


def main():
    """
    Runs the entire program.

    :return: Returns None.
    """
    email_address, password = get_credentials()

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
        group_emails(conn, c, emails, email_address, password)
        verified = False


def get_credentials():
    """
    Gets your email address and password to validate logging in into your account.

    :return: Returns the email address and password.
    """
    email_address = input('Enter your email address: ')
    password = getpass.getpass('Enter your email password: ')
    return email_address, password


def get_email_to_group():
    """
    Takes as input the email address(es) whose emails are to be grouped.

    :return: Returns the email address(es) or if an error occurs returns -1 or False.
    """
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
    """
    Creates a uid table where the uid of the last processed email is saved.

    :return: Returns a connection and a cursor object to the database.
    """
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
    """
    Extracts the uid of an email from a list of uid objects of the type byte.

    :param uid: This is a list of uid objects of the type byte.
    :return: Returns the extracted uid object decoded to the type string from
    the list of uids of the type byte.
    """
    uid_as_list = uid
    _, _, uid_as_byte = uid_as_list[0].split()
    uid = uid_as_byte[:-1]
    uid = uid.decode('utf-8')
    return uid


def create_folder(mail, email):
    """
    Create folders bearing a name that references the email address(es) provided by the user.

    :param mail: This is an imap object that holds a verified connection to your email server.
    :param email: This is a dictionary that contains the email address, the local and domain part of the email
    address.
    :return: Returns the name of the folder.
    """
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
    """
    Copies emails into the respective folders created for each email address.

    :param mail: This is an imap object that holds a verified connection to the email server.
    :param email: This is a dictionary that contains the email address, the local and domain part of the email
    address.
    :param list_of_msg_indexes: This is a list that contains the index of each message of the type byte.
    :param folder_name: The name of the folder to hold emails whose sender address matches the email
    address provided by the user.
    :return: Returns True after the process is completed.
    """
    print('Copying items...')
    for num in reversed(list_of_msg_indexes):
        _, msg_in_bytes = mail.fetch(num, '(RFC822)')
        msg_in_bytes = msg_in_bytes[0][1]
        msg = message_from_bytes(msg_in_bytes)
        if msg['From'] == email["email"]:
            mail.copy(num, folder_name)
    return True


def tracker(conn, c, mail, number_of_emails, list_of_msg_indexes):
    """
    This makes sure all the email addresses or the email address provided by the user
    has been processed completely before saving the uid of the last processed email into the database.

    :param conn: This is a connection object to the database.
    :param c: This is a cursor object to the database.
    :param mail: This is an imap object that holds a verified connection to the email server.
    :param number_of_emails: The number of email addresses provided.
    :param list_of_msg_indexes: This is a list that contains the index of each message of the type byte.
    :return: Returns True after execution.
    """
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


def group_emails(conn, c, emails, email_address, password):
    """
    Runs various custom functions which take part in grouping emails into folders.

    :param conn: This is a connection object to the database.
    :param c: This is a cursor object to the database.
    :param emails: A list containing a dictionary of email address information.
    :param email_address: The users user to login.
    :param password: The users password to login.
    :return: Returns None.
    """
    try:
        host = 'imap.gmail.com'
        mail = imaplib.IMAP4_SSL(host)
        mail.login(email_address, password)
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
    except imaplib.IMAP4.error as e:
        if "b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'" in str(e):
            print('Invalid credentials. Authentication failed.')
    except (socket.gaierror, ConnectionRefusedError, TimeoutError):
        print('An error occurred. Please make sure you have a stable internet connection.')


if __name__ == '__main__':
    main()
