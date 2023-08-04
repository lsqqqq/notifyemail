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
from .tools import Logger
from .notify_backend import NotifyBackend


class NotifyFrontend:
    """
    Notify class called when the main program imports 'notify'. It starts NotifyBackend as a background process.
    It does not run as a separate process but will end together with the main program. 
    Only performing file operations.

    Features:
    - Captures and logs all print outputs from the main program and its threads.
    - Stores specified text and files based on commands.

    Log Storage Structure:
    - Log_Cache.log         : Stores all print logs.
    - Server_Status.log     : Stores monitoring information (defined in NotifyBackend class).
    - Trans_Body.log        : Stores textual instructions to be used as email content when sending notifications.
    - Trans_File.log        : Stores the paths of files to be transmitted.
    - Temp_Zip_File folder  : Stores compressed files (defined in NotifyBackend class).

    Dependencies:
    - class Logger
    - class NotifyFrontend
    """

    def __init__(self, log_root_path, mail_host, mail_user, mail_pass, default_receiving_list, max_log_cnt=5, init_import=False):
        """
        Initialize NotifyFrontend.

        Parameters
        ----------
        log_root_path : str
            The path where you wish to save log files.

        mail_host : str
            The SMTP server hostname, e.g., 'smtp.163.com'.

        mail_user : str
            The email account used for sending notifications, e.g., 'xxxxxx@163.com'.

        mail_pass : str
            The authorization code for the email account. For NetEase Enterprise Email, this is the authorization code.

        default_receiving_list : str or list or tuple
            The default recipient(s) for notifications. It can be a single email address (str) or a list/tuple containing email addresses.

        max_log_cnt : int, optional
            The number of logs to retain for the same program (including current and historical logs).
            Having too many logs might consume excessive memory. Default is 5.
        
        init_import : bool
            Set to True during import.
        """
        self.log_root_path = log_root_path
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.default_receiving_list = default_receiving_list
        self.max_log_cnt = max_log_cnt

        # Only the NotifyFrontend with empty value is called during importing the module.
        if init_import:
            pass

        # If all the value is set, start logging and monitoring.
        elif self.log_root_path and self.mail_host and self.mail_user and self.mail_pass:

            # File save settings
            call_func_name = 'default'

            self.log_creation_path = os.path.join(self.log_root_path, call_func_name)  # log main dir = log root dir + program name.
            self.max_log_under_root_path = self.max_log_cnt  # max log count under log root directory. If exceed, remove earliest log.

            log_folder_name = time.strftime('%Y_%m_%d-%H_%M_%S', time.localtime(time.time()))  # Use current time as sub-folder name.
            self.log_folder_path = os.path.join(self.log_creation_path, log_folder_name)

            # All "print" outputs are saved into this file.
            self.log_cache_path = os.path.join(self.log_folder_path, 'Log_Cache.log')

            # File to save the paths of files to be transferred.
            # Transfer principle: When notify.add_file(file_name) is called, the address of 'file_name' is written to this location.
            # NotifyBackend reads the corresponding file and attaches it to the email after the program ends.
            self.trans_file_path = os.path.join(self.log_folder_path, 'Trans_File.log')

            # File to save the email body text. When notify.add_text("...") is called, the text is saved at this location.
            self.trans_body_path = os.path.join(self.log_folder_path, 'Trans_Body.log')

            # File to save the email sending settings. The recipients of the emails are saved here.
            self.settings_path = os.path.join(self.log_folder_path, 'Settings.log')

            # File to save the function names. This file is used for internal logging purposes.
            self.func_name_path = os.path.join(self.log_folder_path, 'Func_Name.log')

            # Create directories
            if not os.path.exists(self.log_root_path):
                os.mkdir(self.log_root_path)
            if not os.path.exists(self.log_creation_path):
                os.mkdir(self.log_creation_path)
            if os.path.exists(self.log_folder_path):
                os.rmdir(self.log_folder_path)
            os.mkdir(self.log_folder_path)

            self.delete_obsolete_log()  # Remove obsolete logs

            # Redirect print output to the file. When program ends, exit.
            sys.stdout = Logger(self.log_cache_path, path=os.getcwd())  # Normal output
            sys.stderr = Logger(self.log_cache_path, path=os.getcwd())  # Warning output

            # Write into log header
            fileName = time.strftime('LOG_Cache_' + '%Y_%m_%d_%H_%M', time.localtime(time.time()))
            print(fileName.center(60, '*'))

            # Start notify background process
            notify_backend_thread = NotifyBackend(self.log_root_path, log_folder_name, mail_host=self.mail_host,
                                                  mail_user=self.mail_user,
                                                  mail_pass=self.mail_pass, mail_list=self.default_receiving_list)
            notify_backend_thread.start()

        # If you went here, it means you have not given enough parameters.
        else:
            empty_params = \
                [param_name for param_name in ['log_root_path', 'mail_host', 'mail_user', 'mail_pass'] if getattr(self, param_name) is None]
            raise ValueError(f'You have not setup the following parameters: {empty_params}')

    def reboost(self, log_root_path, mail_host, mail_user, mail_pass, default_receiving_list=None, max_log_cnt=5):
        """Re-initialize NotifyFrontend.
        """
        if default_receiving_list == None:
            default_receiving_list = mail_user

        self.__init__(log_root_path=log_root_path, mail_host=mail_host,
                      mail_user=mail_user, mail_pass=mail_pass,
                      default_receiving_list=default_receiving_list, max_log_cnt=max_log_cnt)

    def delete_obsolete_log(self):
        """Remove obsolete log.
        """
        create_time_dict = {}
        create_time_list = []
        for file_name in os.listdir(self.log_creation_path):
            c_time = int(time.mktime(time.strptime(file_name, '%Y_%m_%d-%H_%M_%S')))
            create_time_list.append(c_time)
            create_time_dict[c_time] = file_name
        if len(create_time_list) >= self.max_log_under_root_path - 1:
            create_time_list.sort()
            for c_time in create_time_list[:-self.max_log_under_root_path + 1]:
                shutil.rmtree(os.path.join(self.log_creation_path, create_time_dict[c_time]))
                print('obsolete log deleted: ', create_time_dict[c_time])

    def add_a_text(self, text_input):
        with open(self.trans_body_path, 'a') as file_object:
            file_object.write(text_input + '\n')

    def add_a_file(self, file_dir):
        with open(self.trans_file_path, 'a') as file_object:
            file_object.write(file_dir + '\n')

    def send_log(self, mail_list, call_func_name):
        """
        Write email addresses and the program name to a file for NotifyBackend to access.

        Parameters
        ----------
        mail_list : list or tuple
            The list of email addresses for sending notifications.

        call_func_name : str
            The name of the main program.

        Returns
        -------
        None
        """
        if type(mail_list) in [list, tuple]:  # Multiple recipients
            if type(mail_list) == tuple:
                mail_list = list(mail_list)
            with open(self.settings_path, 'w') as file_object:
                for mail_recv in mail_list:
                    file_object.write(mail_recv + '\n')

        elif type(mail_list) == str:  # Single recipient
            with open(self.settings_path, 'w') as file_object:
                file_object.write(mail_list)

        with open(self.func_name_path, 'w') as file_object:
            file_object.write(call_func_name)

