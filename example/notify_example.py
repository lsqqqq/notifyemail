"""
NotifyEmail Example     Script version Aug 4th 2023


NotifyEmail is a tool for those who want their code and output
be recorded and sent in the email.

Two log files (all python output and a server status log) will be sent in the email
to tell you WHEN and HOW your code ends.

Notice:
 - You need to set up your OWN EMAIL with SMTP, check this out in SMTP ReadME.

To install notifyemail:
 - pip install notifyemail

Official github: 
 - https://github.com/lsqqqq/notifyemail

"""

# 1. Import the package. Nothing will happen here.
import notifyemail as notify


# 2. Setup the environment before running any tasks
notify.setup(mail_host='smtp.163.com', 
             mail_user='xxxxxx@xxx.com', 
             mail_pass='xxxxxx',
             log_root_path='notify_log', 
             mail_list=['xxxxxx@xxx.com'])


# 3. System output will be logged and you may check in your email.
print('Hello world!')
import time
for i in range(5):
    print(f'{i}: Your program is running...')
    time.sleep(1)


# 4. You can use notify.add_text() to add words in the body of the email.
notify.add_text('This is the first line goes into the mail text.')
notify.add_text('This is the second line goes into the mail text.')


# 5. You can use notify.add_file() to add a folder into your email.
# The folder will be compressed and attached to the email after your program ends.
a_file_path = './result_folder'
notify.add_file(a_file_path)


# 6. After meeting an error or for any reason, the program died, notifyemail will try to 
# send the program output to the listed mailboxes. This can help you diagnosis 
# the program issues.
print('Here comes an error!')
something_went_wrong_here

