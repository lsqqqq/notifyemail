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

class NotifyBackend(threading.Thread):
    """
    Background Notify monitor running as a separate process.

    Features:
    - Monitors server performance parameters.
    - Monitors whether the main process is alive.
    - After the main process ends, it packs the log data and sends it to the specified email, and then self-terminates.

    Inputs:
    - log_folder_path : str
        The directory path where log files are stored.

    - mail_host : str
        The SMTP server hostname.

    - mail_user : str
        The email account used for sending notifications.

    - mail_pass : str
        The authorization code for the email account.

    - mail_list : list or tuple
        The list of email addresses for receiving notifications.

    Dependencies:
    - class Logger
    """

    def __init__(self, log_root_path, log_folder_name, mail_host, mail_user, mail_pass, mail_list):
        threading.Thread.__init__(self, name='notify')

        # User-defined monitoring parameters
        self.report_time = 300  # Time interval (in seconds) to calculate and write average values into the log file (300 seconds)
        self.sample_time = 5  # Time interval (in seconds) for each monitoring sample (5 seconds)
        self.max_log_under_root_path = 5  # Maximum number of logs from the same log source

        # Define global variables
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.mail_list = mail_list  # List of email addresses to receive notifications

        call_func_name = 'default'
        self.log_folder_name = log_folder_name  # Log folder name (time-based)
        self.log_root_path = log_root_path  # Root directory for log files
        self.log_folder_path = os.path.join(log_root_path, call_func_name, log_folder_name)  # Log folder directory
        self.finish_process = 0  # Set to 1 after the process ends normally
        self.monitor_process = False  # Monitoring thread status
        self.additional_explain = ''    # Additional explanation, generally includes information like 'compressed file not found'.
                                        # If assigned a value, it will be appended to the email content in Trans_Body.log
        self.start_time = time.time()   # Record the start time of the monitoring process

        # Start server monitoring process
        self.start_monitor(self.log_folder_path, log_name='Server_Status.log',
                           report_time=self.report_time, sample_time=self.sample_time)

    def run(self):
        """Check if the main process is alive.
        """
        while 1:
            # Check if alive every self.sample_time.
            for i in threading.enumerate():
                if i.name == "MainThread" and not i.is_alive():  # Perform post-processing tasks after the main thread ends.
                    self.stop_monitor()  # End server performance monitoring.
                    self.send_email()
                    return
            time.sleep(self.sample_time)

    '''
    ****************************************
    Server performance monitoring functions
    ****************************************
    '''

    def start_monitor(self, log_dir, log_name='server_status.log', report_time=300, sample_time=5):
        """
        Start monitor function.

        Parameters
        ----------
        log_dir : str
            The path where you wish to save log files.

        log_name : str, optional
            The name of the log file (default is 'server_status.log').

        report_time : int, optional
            Time interval (in seconds) between log reports (default is 300 seconds).

        sample_time : int, optional
            Time interval (in seconds) between performance samples (default is 5 seconds).
        """
        self.monitor_process = threading.Thread(target=self.server_monitor_process, daemon=True,
                                                args=(log_dir, log_name, report_time, sample_time))
        self.monitor_process.start()

    def stop_monitor(self):
        if bool(self.monitor_process):
            self.finish_process += 1
            self.monitor_process.join()  # Waiting for monitor_process finished
        print("finished")

    def server_monitor_process(self, log_dir, log_name='server_status.log', report_time=300, sample_time=5):
        """
        Main function for server monitoring.

        Parameters
        ----------
        log_dir : str
            The directory where the log files will be saved.

        log_name : str, optional
            The name of the log file (default is 'server_status.log').

        report_time : int, optional
            Time interval (in seconds) between writing mean values to the log (default is 300 seconds).

        sample_time : int, optional
            Time interval (in seconds) between each monitoring sample (default is 5 seconds).

        Returns
        -------
        None
        """
        next_time_to_report = report_time

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.write_information_to_log(log_dir, log_name, info_type='init', report_time=report_time,
                                      sample_time=sample_time)
        print('start monitoring:)')

        cpu_list = []
        mem_list = []

        cpu_avg_list = []
        mem_avg_list = []
        cpu_max_list = []
        mem_max_list = []
        while True:
            cpu_list.append(psutil.cpu_percent(interval=sample_time, percpu=True))
            mem_list.append(psutil.virtual_memory().percent)
            next_time_to_report -= sample_time

            # Save and exit after process ends
            if self.finish_process == 1:
                cpu_avg_list.append(self.calc_avg_cpu_usage_percentage(cpu_list))
                mem_avg_list.append(self.calc_avg_mem_usage_percentage(mem_list))
                cpu_max_list.append(self.calc_max_cpu_usage(cpu_list))
                mem_max_list.append(max(mem_list))
                self.save_server_log(cpu_avg_list[-1], mem_avg_list[-1], log_dir, log_name)

                cpu_avg = self.calc_avg_mem_usage_percentage(cpu_avg_list)
                mem_avg = self.calc_avg_mem_usage_percentage(mem_avg_list)
                cpu_max = self.calc_avg_mem_usage_percentage(cpu_max_list)
                mem_max = self.calc_avg_mem_usage_percentage(mem_max_list)
                self.write_information_to_log(log_dir, log_name, info_type='finish',
                                              cpu_avg=cpu_avg, mem_avg=mem_avg, cpu_max=cpu_max, mem_max=mem_max)
                return 0

            # Normal save
            elif next_time_to_report <= 0:
                cpu_avg_list.append(self.calc_avg_cpu_usage_percentage(cpu_list))
                mem_avg_list.append(self.calc_avg_mem_usage_percentage(mem_list))
                cpu_max_list.append(self.calc_max_cpu_usage(cpu_list))
                mem_max_list.append(max(mem_list))
                self.save_server_log(cpu_avg_list[-1], mem_avg_list[-1], log_dir, log_name)
                cpu_list = []
                mem_list = []
                next_time_to_report = report_time

    def calc_avg_cpu_usage_percentage(self, cpu_usage_list_divided_by_time):
        avg_cpu_usage = 0
        cnt = 0
        for _sample in cpu_usage_list_divided_by_time:
            for single_cpu_percentage in _sample:
                avg_cpu_usage += single_cpu_percentage
                cnt += 1
        avg_cpu_usage = avg_cpu_usage / cnt
        return round(avg_cpu_usage, 2)

    def calc_max_cpu_usage(self, cpu_usage_list_divided_by_time):
        max_cpu_usage = 0
        for _sample in cpu_usage_list_divided_by_time:
            avg_usage = 0
            for single_cpu_percentage in _sample:
                avg_usage += single_cpu_percentage
            avg_usage /= len(_sample)
            if avg_usage > max_cpu_usage:
                max_cpu_usage = avg_usage
        return round(max_cpu_usage, 2)

    def calc_avg_mem_usage_percentage(self, mem_usage_list_divided_by_time):
        avg_mem_usage = 0
        for _sample in mem_usage_list_divided_by_time:
            avg_mem_usage += _sample
        avg_mem_usage = avg_mem_usage / len(mem_usage_list_divided_by_time)
        return round(avg_mem_usage, 2)

    def save_server_log(self, cpu_usage, mem_usage, log_dir, log_name):
        now_time = time.strftime(f'%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        format_save = 'Time: {:20s} | CPU: {:6s} | Mem: {:6s} '.format(now_time, str(cpu_usage), str(mem_usage))
        with open(os.path.join(log_dir, log_name), mode="a", encoding="utf-8") as f:
            f.write(format_save + '\n')
            f.close()

    def write_information_to_log(self, log_dir, log_name, info_type, report_time=60, sample_time=5,
                                 cpu_avg='', mem_avg='', cpu_max='', mem_max=''):
        """
        Write statistical information to the beginning or end of the log.

        Parameters
        ----------
        log_dir : str
            The directory where the log files are saved.

        log_name : str
            The name of the log file.

        info_type : str
            The type of information to write. It can be 'start' to write at the beginning or 'end' to write at the end of the log.

        report_time : int, optional
            Time interval (in seconds) between statistical reports (default is 60 seconds).

        sample_time : int, optional
            Time interval (in seconds) between each monitoring sample (default is 5 seconds).

        cpu_avg : str, optional
            The average CPU usage to be written to the log.

        mem_avg : str, optional
            The average memory usage to be written to the log.

        cpu_max : str, optional
            The maximum CPU usage to be written to the log.

        mem_max : str, optional
            The maximum memory usage to be written to the log.

        Returns
        -------
        None
        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if info_type == 'init':
            status_statement = '============================================\n' \
                           'Monitoring Start Time:   %s\n' \
                           'Sample Interval (s):    %s  | Log Write Interval (s):   %s  \n' \
                           '============================================' % \
                           (current_time, str(sample_time), str(report_time))
        elif info_type == 'finish':
            status_statement = '============================================\n' \
                           'Monitoring End Time:     %s\n' \
                           'Average CPU Usage:       %s  | Average Memory Usage:   %s\n' \
                           'Maximum CPU Usage:       %s  | Maximum Memory Usage:   %s\n' % \
                           (current_time, str(cpu_avg), str(mem_avg), str(cpu_max), str(mem_max))
        else:
            return 1
        with open(os.path.join(log_dir, log_name), mode="a", encoding="utf-8") as f:
            f.write(status_statement + '\n')
            f.close()

    '''
    ****************************************
    File read & send functions
    ****************************************
    '''

    def send_email(self):
        """Send email.
        """

        # Log format
        log_type = ".log"

        log_cache_path = os.path.join(self.log_folder_path, 'Log_Cache.log')
        trans_file_path = os.path.join(self.log_folder_path, 'Trans_File.log')
        trans_body_path = os.path.join(self.log_folder_path, 'Trans_Body.log')
        settings_path = os.path.join(self.log_folder_path, 'Settings.log')
        trans_file_zip_path = os.path.join(self.log_folder_path, 'Temp_Zip_File')  # Compressed and to be transfered files location
        server_status_path = os.path.join(self.log_folder_path, 'Server_Status.log')  # Server monitor log location
        func_name_path = os.path.join(self.log_folder_path, 'Func_Name.log')

        # Setup mail info
        if os.path.exists(settings_path):
            self.mail_list = []
            for mail_recv in open(settings_path, 'r'):
                self.mail_list.append(re.sub(r'\n', '', mail_recv))

        # Setup time
        time_start = self.start_time
        time_end = time.time()

        # Get server hostname
        source_server = self.get_host_name()

        # Finished, make a conclusion for running status
        print('\n' + '=' * 60)
        print("Processing finished !")
        print("start time:", time.strftime('%Y_%m_%d  %H:%M:%S', time.localtime(time_start)))
        print("end time:", time.strftime('%Y_%m_%d  %H:%M:%S', time.localtime(time_end)))
        print("source:", source_server)

        # Setup log filename
        try:
            with open(func_name_path, 'r') as l:
                call_func_name = l.read()
                l.close()
        except Exception as e:
            print('func send_log() has not called, use default func name: ', e)
            call_func_name = 'default'
        processing_log_name = call_func_name + '__' + time.strftime('%Y_%m_%d-%H_%M_%S',
                                                                    time.localtime(time_start)) + '_log'

        # Setup mail title
        mail_title = '[' + source_server + '  LOG] ' + processing_log_name

        # Setup mail content
        message = MIMEMultipart()
        message['Subject'] = mail_title
        message['From'] = self.mail_user

        # Setup receipient (or recipients)
        if len(self.mail_list) > 1:
            message['To'] = ";".join(self.mail_list)
        elif len(self.mail_list) == 1:  # If only one mailbox is specified, send to this mailbox
            message['To'] = self.mail_list[0]
        else:
            print("mail_list problem occured!")
            return -1

        # Setup mail body text
        running_info = "start time: %s \nend time: %s \nsource: %s \n=================\n\n" % (
            time.strftime('%Y_%m_%d  %H:%M:%S', time.localtime(time_start)),
            time.strftime('%Y_%m_%d  %H:%M:%S', time.localtime(time_end)),
            self.get_host_name()
        )

        # Tackle the encoding difference in Windows, MacOS and Linux
        if os.path.exists(trans_body_path):
            try:
                with open(trans_body_path, 'r', encoding='utf-8') as l:
                    trans_body_content = l.read()
                    l.close()
                running_info += ('\n' + trans_body_content)
            except:
                with open(trans_body_path, 'r', encoding='gb2312') as l:
                    trans_body_content = l.read()
                    l.close()
                running_info += ('\n' + trans_body_content)
        message.attach(MIMEText(running_info, 'plain', 'utf-8'))

        # Manage appendixs
        self.prepare_trans_file()  # Compress user specified files (if exists)
        if os.path.exists(trans_file_zip_path):
            for zip_file in os.listdir(trans_file_zip_path):
                zip_file_full_path = os.path.join(trans_file_zip_path, zip_file)
                with open(zip_file_full_path, 'rb') as Af:
                    file = Af.read()
                try:
                    Af.close()
                    # Add appendix
                    log_part = MIMEText(file, 'base64', 'utf-8')
                    log_part["Content-Type"] = 'application/octet-stream'
                    # filename is the name shown in the email.
                    log_part["Content-Disposition"] = 'attachment; filename="%s"' % zip_file
                    message.attach(log_part)
                except:
                    print("Erro occur in adding additional file:", zip_file)
                else:
                    print("An additional file has been added to the mail:", zip_file)

        # Block log generation
        # (stdout has been redefined as the Logger class during the import of notify,
        # so we directly call the functions of the Logger class here)
        sys.stdout.close_log_and_put_back()

        # Get print output: processing_log
        try:
            # Read log file (as a text appendix file)
            with open(log_cache_path, 'r', encoding='UTF-8') as l:
                processing_log = l.read()
                l.close()
            if processing_log[0] is not '*':
                print("processing log title erro")
        except Exception as e:
            print("processing log status erro: ", e)
            return -1
        else:
            print("processing log catched")

        # Read server log: server_log
        try:
            with open(server_status_path, 'r', encoding='UTF-8') as f:
                server_log = f.read()
                f.close()
            if server_log[0] is not '=':
                print("server log title erro")
        except Exception as e:
            print("server log status erro: ", e)
            return -1
        else:
            print("server log catched")

        try:
            # Appendix 1: processing_log
            log_part = MIMEText(processing_log, 'base64', 'utf-8')
            log_part["Content-Type"] = 'application/octet-stream'
            file = processing_log_name + log_type
            log_part[
                "Content-Disposition"] = 'attachment; filename="%s"' % file
            message.attach(log_part)

            # Appendix 2: server_log
            log_part = MIMEText(server_log, 'base64', 'utf-8')
            log_part["Content-Type"] = 'application/octet-stream'
            file = 'server_status' + log_type
            log_part[
                "Content-Disposition"] = 'attachment; filename="%s"' % file
            message.attach(log_part)

            # Instantiation, which is also the login process.
            smtp = smtplib.SMTP_SSL(self.mail_host, timeout=3000)
            smtp.ehlo(self.mail_host)
            smtp.login(self.mail_user, self.mail_pass)
            smtp.sendmail(self.mail_user, self.mail_list, message.as_string())
            smtp.quit()
            print('Log email sent successfully, title: ', mail_title)
            print('If not found, please check the spam folder :)')

            # Move log & remove obsolete data
            try:
                sys.stderr.close_log_and_put_back()  # Stop warning log generation
            except:
                pass

            new_root_path = os.path.join(self.log_root_path, call_func_name)
            new_folder_path = os.path.join(new_root_path, self.log_folder_name)
            if not os.path.exists(new_root_path):
                os.mkdir(new_root_path)
            self.delete_obsolete_log(new_root_path)
            shutil.move(self.log_folder_path, new_root_path)
        except Exception as e:
            print('Failed to send the mail: ', e)

    def prepare_trans_file(self):
        """
        Prepare files for email transmission (if any).
        Log file structure:
        - Log_Cache.log        Save all print logs.
        - Server_Status.log    Save monitoring information (defined in NotifyBackend class).
        - Trans_Body.log       Save textual instructions, used as the email body when sending.
        - Trans_File.log       Save addresses of files to be transmitted.
        - Temp_Zip_File        Folder, used to save compressed files (defined in NotifyBackend class).
        :return:
        """
        # Read the directory of files to be transferred
        trans_file_log_path = os.path.join(self.log_folder_path, 'Trans_File.log')  # Trans_File.log文件地址

        if os.path.exists(trans_file_log_path):  # If Trans_File.log exists, the read line by line

            # Create compress directory Temp_Zip_File
            trans_file_zip_path = os.path.join(self.log_folder_path, 'Temp_Zip_File')
            if not os.path.exists(trans_file_zip_path):
                os.mkdir(trans_file_zip_path)

            # Read all files and compress them into Temp_Zip_File
            for file_path in open(trans_file_log_path, 'r'):
                file_path = re.sub(r'\n', '', file_path)
                full_path = os.path.join(os.getcwd(), file_path)
                if os.path.exists(full_path):
                    zip_file_name = re.findall(r'[^/\\]+$', file_path)[0]  # zip file name (same as original file name)
                    zip_err = self.zipDir(full_path, os.path.join(trans_file_zip_path, zip_file_name))  # Compress & save
                    if zip_err:
                        print('zip error! details below: \n', zip_err)
                else:
                    print('cannot zip file: ', file_path)

    def zipDir(self, dirpath, outFullPath):
        """
        Compresses the specified folder to the specified path.

        Parameters
        ----------
        dirpath : str
            Target folder path: 1212/12/c

        outFullPath : str
            Output path for the compressed file. Example: 'aaa/bbb/c.zip'
        """
        try:
            zip = zipfile.ZipFile(outFullPath + '.zip', 'w', zipfile.ZIP_DEFLATED)
            # Directory: iterally compress
            if os.path.isdir(dirpath):
                for path, dirnames, filenames in os.walk(dirpath):
                    # only compress the files and folders under the target folder (including the parent folder itself)
                    parent_path = os.path.abspath('.')  # Parent folder
                    fpath = path.replace(dirpath, '')  # Child folder
                    for filename in filenames:
                        zip.write(os.path.join(path, filename),
                                  os.path.join(fpath, filename))
                zip.close()
            # File: compress directly
            elif os.path.isfile(dirpath):
                zip.write(dirpath, re.findall(r'[^/\\]+$', outFullPath)[0])
                zip.close()
        except Exception as e:
            return e
        return 0

    def delete_obsolete_log(self, log_root_path):
        """
        Check and remove early logs.

        Parameters
        ----------
        log_root_path : str
            The root path where logs are stored. This function will check for early logs
            in this directory and remove them if necessary.
        """
        create_time_dict = {}
        create_time_list = []
        for file_name in os.listdir(log_root_path):
            c_time = int(time.mktime(time.strptime(file_name, '%Y_%m_%d-%H_%M_%S')))
            create_time_list.append(c_time)
            create_time_dict[c_time] = file_name
        if len(create_time_list) >= self.max_log_under_root_path - 1:
            create_time_list.sort()
            for c_time in create_time_list[:-self.max_log_under_root_path + 1]:
                shutil.rmtree(os.path.join(log_root_path, create_time_dict[c_time]))
                print('obsolete log deleted: ', create_time_dict[c_time])

    def get_host_name(self):
        """Get server hostname
        """
        return socket.gethostname()

