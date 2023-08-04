import threading
import os
import psutil
import re
import socket
import sys
import time
import shutil
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Logger(object):
    """Redirect print to designated file
    """

    def __init__(self, processing_log_name="LOG_Default.log", path="./"):
        self.ori_stdout = sys.stdout
        self.terminal = sys.stdout
        self.log = open(os.path.join(path, processing_log_name), "a", encoding='utf8', )
        self.start_time = time.time()
        self.text_content = []
        self.additional_file_list = []

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

    def close_log_and_put_back(self):
        self.log.close()
        sys.stdout = self.ori_stdout  # ori_stdout is the original sys.stdout, now used for recovery


def _setup(notify_frontend, 
           mail_host=None, 
           mail_user=None,
           mail_pass=None, 
           default_receiving_list=None,
           log_root_path=None,
           max_log_cnt=5, 
           mail_list=None,
           default_reciving_list=None):
    """Setup notifyemail.
    """
    # At least one is needed to specify the mail list.
    assert default_reciving_list or default_receiving_list or mail_list

    # Alias for compatibility
    if default_reciving_list:
        default_receiving_list = default_reciving_list

    default_receiving_list = default_receiving_list \
        if default_receiving_list else mail_list
    mail_list = mail_list if mail_list else default_receiving_list

    _Reboost(notify_frontend=notify_frontend, 
             mail_host=mail_host, mail_user=mail_user,
             mail_pass=mail_pass, 
             default_receiving_list=default_receiving_list, 
             log_root_path=log_root_path, 
             max_log_cnt=max_log_cnt)
    _send_log(mail_list=None, 
              notify_frontend=notify_frontend)


def _Reboost(notify_frontend, mail_host=None, 
             mail_user=None,
             mail_pass=None, 
             default_receiving_list=None, 
             log_root_path=None, 
             max_log_cnt=5,
             default_reciving_list=None):
    """
    Restart the notify background process.

    Parameters
    ----------

    mail_host : str
        The SMTP server hostname. Default is None.

    mail_user : str
        The email account used for sending notifications. Default is None.

    mail_pass : str
        The authorization code for the email account. Default is None.

    log_root_path : str
        The root path where log files will be saved. Default is None.

    notify_frontend : notify class
        The notify class object used for sending notifications.

    default_receiving_list : str or list, optional
        The default recipient(s) for notifications. It can be a single email address (str) 
        or a list of email addresses. Default is None.

    max_log_cnt : int, optional
        The maximum number of logs that Notify will not auto-delete. 
        This is intended to save space on the local drive. Default is 5.
    
    default_reciving_list : str or list, optional
        The alias of default_receiving_list.
    
    Returns
    -------
    None
        Restarts the notify background process and prints the following information:
        - The log root path.
        - The mail user (email account).
        - The default receiving list for notifications.
        - The number of logs that will not be auto-deleted.
    """
    # Alias for compatibility
    if default_reciving_list:
        default_receiving_list = default_reciving_list

    # Restart notify background process
    notify_frontend.reboost(log_root_path=log_root_path, mail_host=mail_host,
                            mail_user=mail_user, mail_pass=mail_pass,
                            default_receiving_list=default_receiving_list, max_log_cnt=max_log_cnt)
    print('Notifyemail initialized.')
    print(f' - log_root_path:          {notify_frontend.log_root_path}')
    # print('mail_host', notify_frontend.mail_host)
    print(f' - mail_user:              {notify_frontend.mail_user}')
    # print('mail_pass', notify_frontend.mail_pass)
    print(f' - default_receiving_list: {notify_frontend.default_receiving_list}')
    # print('max_log_cnt', notify_frontend.max_log_cnt)


def _add_text(text_input, notify_frontend=None):
    """
    Set the default mail content.

    Parameters
    ----------
    text_input : str
        Text content to be added.

    notify_frontend : object, optional
        Notify class (not relevant to the caller).

    Returns
    -------
    None
    """

    if notify_frontend.log_root_path == None or notify_frontend.mail_host == None \
            or notify_frontend.mail_user == None or notify_frontend.mail_pass == None:
        raise Exception('\nPlease reset Notify frontend by:\nUsing notify.Reboost(xxx)' +
                        ' RIGHT AFTER you FIRST import Notify ' +
                        'your need to set \n log_root_path= str, the place you wish to save log files' +
                        '\nmail_host= str, smtp server like smtp.163.com' +
                        '\nmail_user = str, send mail account like xxxxxxx@163.com' +
                        '\nmail_pass = str, the authorization code from the server' +
                        '\nyou can set default_receiving_list = str(an email address) or a list / tuple containing email ' +
                        'address, NOTICE by defult it will be send back to your mail_user account if you dont set this' +
                        '\nyou can set max_log_cnt = int, this is the amount of logs the notify will not auto delete ' +
                        'this is aming for saving the zoom of your local driver')

    if bool(notify_frontend):
        notify_frontend.add_a_text(text_input=text_input)


def _add_file(file_dir, notify_frontend=None):
    """
    Add email attachments.

    Parameters
    ----------
    file_dir : str
        The path of the attachments to be added. It can be a file or a folder (will be automatically zipped).

    notify_frontend : object, optional
        notify class (not relevant to the caller).

    Returns
    -------
    None
    """
    if notify_frontend.log_root_path == None or notify_frontend.mail_host == None \
            or notify_frontend.mail_user == None or notify_frontend.mail_pass == None:
        raise Exception('\nPlease reset Notify frontend by:\nUsing notify.Reboost(xxx)' +
                        ' RIGHT AFTER you FIRST import Notify ' +
                        'your need to set \n log_root_path= str, the place you wish to save log files' +
                        '\nmail_host= str, smtp server like smtp.163.com' +
                        '\nmail_user = str, send mail account like xxxxxxx@163.com' +
                        '\nmail_pass = str, the authorization code from the server' +
                        '\nyou can set default_receiving_list = str(an email address) or a list / tuple containing email ' +
                        'address, NOTICE by defult it will be send back to your mail_user account if you dont set this' +
                        '\nyou can set max_log_cnt = int, this is the amount of logs the notify will not auto delete ' +
                        'this is aming for saving the zoom of your local driver')
    notify_frontend.add_a_file(file_dir=file_dir)
    print(file_dir, " has been added to the mail attachment list.")


def _send_log(mail_list=None, notify_frontend=None):
    """
    Set the recipient email address(es) to receive logs. You can set this at any location in the code, 
    and the email will be sent to the last specified recipient after the program execution completes.

    Parameters
    ----------
    mail_list : str or list, optional
        The recipient(s) for the logs. It can be a single email address (str) or a list of email addresses.

    notify_frontend : object, optional
        Notify class (not relevant to the caller).

    Returns
    -------
    None
    """

    if notify_frontend.log_root_path == None or notify_frontend.mail_host == None \
            or notify_frontend.mail_user == None or notify_frontend.mail_pass == None:
        raise Exception('\nPlease reset Notify frontend by:\nUsing notify.Reboost(xxx)' +
                        ' RIGHT AFTER you FIRST import Notify ' +
                        'your need to set \n log_root_path= str, the place you wish to save log files' +
                        '\nmail_host= str, smtp server like smtp.163.com' +
                        '\nmail_user = str, send mail account like xxxxxxx@163.com' +
                        '\nmail_pass = str, the authorization code from the server' +
                        '\nyou can set default_receiving_list = str(an email address) or a list / tuple containing email ' +
                        'address, NOTICE by defult it will be send back to your mail_user account if you dont set this' +
                        '\nyou can set max_log_cnt = int, this is the amount of logs the notify will not auto delete ' +
                        'this is aming for saving the zoom of your local driver')

    if mail_list == None:
        mail_list = notify_frontend.default_receiving_list
    if bool(mail_list):
        # call_func_name = sys._getframe(1).f_code.co_filename.split('/')[-1]  # Get program main directory
        # call_func_name = re.findall(r'[^/\\]+$', call_func_name)[0].split('.py')[0]

        # Fetch the first .py code that is calling this function. (TODO: need to test on Windows)
        back_frame = sys._getframe()
        while back_frame.f_back:
            back_frame = back_frame.f_back
        call_func_name = os.path.basename(back_frame.f_code.co_filename).split('.')[0]

        notify_frontend.send_log(mail_list, call_func_name)
