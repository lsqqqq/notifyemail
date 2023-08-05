"""
notifyemail-1.1.0

Notifyemail is a package that sends notifications via email when your code finishes 
running on a remote server, even within a Local-Area-Network (LAN). 
It also works well with other environments like Google Colab and notifies you of 
the results when program finished.

Hope it can do some help for your project :)

Special thanks:
 - 吕尚青
 - 张天翊
 - 雷言理
 - 吴雨卓
"""

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
from .notify_backend import NotifyBackend
from .notify_frontend import NotifyFrontend
from .tools import Logger, _setup, _Reboost, _add_text, _add_file, _send_log


# By default, start notify background process with empty values
notify_frontend = NotifyFrontend(log_root_path=None, mail_host=None,
                                 mail_user=None, mail_pass=None,
                                 default_receiving_list=None, max_log_cnt=5, 
                                 init_import=True)


### Mail settings ###
def setup(notify_frontend=notify_frontend, *args, **kwargs):
    """
    Configure email settings, start the notify background process.

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

    default_receiving_list : str or list, optional
        The default recipient(s) for notifications. It can be a single email address (str) 
        or a list of email addresses. Default is None.

    max_log_cnt : int, optional
        The maximum number of logs that Notify will not auto-delete. 
        This is intended to save space on the local drive. Default is 5.
    
    default_reciving_list : str or list, optional
        The alias of default_receiving_list.

    mail_list : str or list, optional
        The recipient(s) for the logs. It can be a single email address (str) or a list of email addresses.

    notify_frontend : notify class, optional
        The notify class object used for sending notifications.
    
    Returns
    -------
    None
        Start the notify background process and prints the following information:
        - The log root path.
        - The mail user (email account).
        - The default receiving list for notifications.
        - The number of logs that will not be auto-deleted.
    """
    _setup(notify_frontend=notify_frontend, *args, **kwargs)

### Add text or files ###

def add_text(text_input, notify_frontend=notify_frontend):
    return _add_text(text_input, notify_frontend=notify_frontend)

def add_file(file_dir, notify_frontend=notify_frontend):
    return _add_file(file_dir, notify_frontend=notify_frontend)

### Compatible functions ###

def Reboost(notify_frontend=notify_frontend, *args, **kwargs):
    _Reboost(notify_frontend=notify_frontend, *args, **kwargs)

def send_log(mail_list=None, notify_frontend=notify_frontend):
    return _send_log(mail_list=mail_list, notify_frontend=notify_frontend)