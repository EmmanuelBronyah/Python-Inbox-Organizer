# Python Inbox Organizer
This python inbox organizer is a command-line python program that takes
as input a valid email address, searches through the mails in the
inbox folder of the user's gmail account and groups all emails received
from that email address into a special folder or label. You
must provide your email address and password which the program
uses to log into your account and perform the automation.

## Features of the inbox organizer
1. **Takes email address or addresses to group:** The program takes a 
valid email address or addresses and groups all emails received by 
these addresses. If more than one email address is provided, these 
email addresses must be separated with a space after a comma else an
error will be thrown. For example: johncane@email.com, sissi@email.com.
2. **Creates a unique identifier table:** The program creates a uid 
table where the last processed email message uid is stored. This is to
keep track of email messages yet to be received.
3. **Retrieves uid:** The uid of the last processed email is retrieved 
and saved in the uid table in the database.
4. **Creates folders or labels:** The program creates folders bearing 
a name reference of the email addresses whose messages are to be 
grouped and copies all the matching emails into their respective folders.
5. **Copies emails:** The program copies all the emails whose sender
address matches the email address provided by the user.
6. **Tracker:** The program implements a tracker function that makes
sure all the email addresses or the email address provided has been 
processed completely before saving the uid of the last processed email
into the database.
7. **Groups emails:** This feature of the program goes through the
necessary configurations and logic required to login, copy all
emails, create folders and other useful requirements needed to
complete all the processes.

## Getting Started
1.Clone the repository to your machine.
```shell
git clone https://github.com/EmmanuelBronyah/Python-Inbox-Organizer.git
```
2. Navigate to the project directory
```shell
cd inbox-categorizer
```
3. Run the program
```shell
python main.py
```

## Usage
* When you run the program you will be prompted to provide
your email address and password. The password will not be
visible as you type. The program then after prompts 
you to provide a valid email address or email addresses
that the emails in the inbox folder is grouped by. 
If two or more valid email addresses are provided, 
these email addresses must be separated with a 
space after a comma else an error will be thrown. 

## Example 
1. Providing your email address and password for authentication.
```shell
Enter your email address: mike@email.com
Enter your email password: 
```

2. When the authentication fails.
```shell
Enter the email(s) you want to group: john@email.com, lad@email.com
Invalid credentials. Authentication failed.
```

2. Providing email addresses.
```shell
Enter the email(s) you want to group: john@email.com, lad@email.com
Copying items...
Messages from john@email.com has been copied to Emails_from_john folder.
Copying items...
Messages from lad@email.com has been copied to Emails_from_lad folder.
Tracked.
```
3. Providing wrong email addresses.
```shell
Enter the email(s) you want to group: wepfjpme@
Enter a valid email.
```
4. Providing two valid email addresses not in the specified format.
```shell
Enter the email(s) you want to group: john@email.com,lad@email.com
List emails in the specified format.
```

## License
This project is licensed under the MIT license.

## Acknowledgement.
Built by Bronyah Emmanuel.