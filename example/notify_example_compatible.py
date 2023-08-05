"""
NotifyEmail Example     Script version Apr 18th 2022

Simpely use pip to get our notifyemail tool!
pip install notifyemail

Official github: https://github.com/lsqqqq/notifyemail


NotifyEmail is a tool for those who want their code and output
be recorded and sent in the email.

2 log files (all python output and a server status log) will be sent in the email
to tell you WHEN and HOW your code ends.

many other useful like file packing and email writing are developed here too.


Notice:
You need to set up your OWN EMAIL with SMTP, check this out in SMTP ReadME.
"""

# A thousand thanks for you as now you are reading this.

# 1. the import will trigger the monitoring process, so use this in the code line instead of in the title.
import notifyemail as notify


# 2. Please reset Notify frontend by this, Right After you first import Notify
notify.Reboost(mail_host='smtp.163.com', mail_user='xxxxxx@xxx.com', # set the smtp Email server info
               mail_pass='xxxxxx', default_reciving_list=['xxxxxx@xxx.com'], # set the smtp password and default_reciving_list
               log_root_path='notify_log', max_log_cnt=5)  # set the log path, by default in ./log

# 3. Your Own magical codes
print('Hello world!')
for i in range(42):
    print(i)  # all system output, including the erro will be record into the log attachment.
print('A thousand thanks for you as now you are reading this.')


# 4. You can use notify.add_text() to add words in the Email paper.
notify.add_text('this line goes into the mail paper you see')
# you can use it as many times as you like
# you can use it anywhere After the notify.Reboost()


# 5. You can use notify.add_file() to add words in Email paper.
A_file_path = './result_folder'
notify.add_file(A_file_path)  # the path will be zip and save as attachment in the Email
# you can use many times as you like
# you can use anywhere After the notify.Reboost()


# 6. use notify.send_log() to set the mailing user(s), leave blank if you want the default_reciving_list as reader(s)
notify.send_log()
# you can use anywhere After the notify.Reboost(),
# you may meet erro with out the call of notify.send_log(), but its fine-working, relex, we are working on it.


# 3. Your Own magical codes after the notify funcs still working and will be recorded.
print('Hello world, Again!')
for i in range(3):
    print(i, 'all system output, including the erro will be recorded into the log attachment.')

    print('A thousand thanks for you as now you are reading this, Again.')