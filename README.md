# notifyemail

Notifyemail is a project based on our demand of sending email to inform us when the code is fished runing on a remote server, for example: CoLab.

You can now simply use this module to send email with text and other component like pics as attachment files when the main code finished running.

You can also use this to transmit files from a remote 'safe' server equipt with a sand box / castle machine.


# USAGE information

Firstly use pip to install our module:  pip install notifyemail

Then you need to set up your OWN EMAIL with SMTP, check this out in SMTP ReadME

After these simple setting you can now follow the tips to use our module in your code.

# Step 1 import and Reboost
需要监控的程序可在启动时用如下代码调用本功能，注意，首先需要reboost：

import notifyemail

/# Please reset Notify frontend by this Right After you first import Notify 先使用Reboost设置发件信息等，参考如下:

notifyemail.Reboost(mail_host='smtp.163.com', mail_user='xxxx@163.com',mail_pass='xxxx', default_receivers='xxx@163.com', log_root_path='log', max_log_cnt=5)
               
               
In notifyemail.Reboost() your need to set:

log_root_path= str, the place you wish to save log files

mail_host= str, smtp server like smtp.163.com

mail_user = str, send mail account like xxxxxxx@163.com

mail_pass = str, the authorization code from the server

you can set default_receing_list = str(an email address) or a list / tuple containing email address,

NOTICE by defult it will be send back to your mail_user account if you dont set this

you can set max_log_cnt = int, this is the amount of logs the notify will not auto delete

this is aming for saving the zoom of your local driver

# Step 2 your code blocks... 
程序代码
...


# Step 3 Add text in the email use this, you can use many times 
在邮件里新增一段文本，可多次用

notifyemail.add_text("whatever u want to say")


# Step 4 Add file/folder in the email use this, you can use many times,the folder will be zipped by our system
追加邮件附件，可以是文件/文件夹的文件路径（会自动zip），只需要在任意位置调用这个函数即可，可多次用,添加多个附件

notifyemail.add_file(file_name）
...


# Step 5 In the process if you wish to send email to other address, use this 
如果需要更改需要发送邮件的邮箱可以用这个，输入为空则为default list。
notifyemail.send_log(xxx)   # str (an email address) or list / tuple containing multiple email address (str) is allowed

# we recomend you to use this at the end of your code, this can update log name information in email
notifyemail.send_log()  # empty
/# 在自己代码中的任意位置调用就行。注意：如果不调用，则邮件中的程序名为default，且自动发送给默认邮箱



# update INFO
-------------------------------------------------------------------------------
版本 8月 20日 02：55  修改了调用逻辑
这个文件用来自动发送 输出log + 性能监控log + 追加的文件 到指定邮箱列表中
主要作者：吕尚青 张天翊 雷言理

-------------------------------------------------------------------------------
# Reciving INFO

用例：

公邮：xxx@163.com

密码：xxx

如果想只发给自己，就把自己邮箱写进去：在自己代码中任意位置使用，以最后一次调用为准

notifyemail.send_log(“1111@111.com”)

如果要发给多人，请传入一个包含多个str的元组/列表。

不写发给谁的话，默认会发给一个默认列表中的所有人，公邮在默认列表中。

发件邮箱：xxx@163.com

密码：xxx

-------------------------------------------------------------------------------

说明：

输出监控日志格式：

*****************LOG_Cache_2020_12_31_01_01*****************

内容

内容

内容

start time: 2020_12_31  01:01:14

end time: 2020_12_31  01:02:04

source: server name

-------------------------------------------------------------------------------

性能监控日志格式：

============================================
监控开始时间:    2021-01-29 03:24:34

采样间隔(s):  5  | 计算均值写入日志间隔(s):   300

============================================

时间: 2021-01-29 03:24:39   | CPU平均占用率: 3.86  | 内存占用率: 75.4

============================================
监控结束时间:    2021-01-29 03:24:39

平均CPU占用率:   3.86  | 平均内存占用率:  75.4

最大CPU占用率:   3.86  | 最大内存占用率:  75.4

-------------------------------------------------------------------------------
2021.1.1 17:00  更新内容：本地日志文件保存在程序目录下的log文件夹内

2021.1.2 11:00  修复了计算均值写入日志间隔的bug

2021.1.29 13:30  修复了程序出错时无法正常发邮件的问题

2021.1.30 13:30 增加了自动清空旧日志的功能（可设置）
                
2021.2.2 01:30   修复了程序名显示错误的问题

2021.7.27 11:30   修复了公邮的问题

2021.8.20 02:30   重写了调用逻辑，增加reboost功能

2021.8.21 11:30   推广为pip库

-------------------------------------------------------------------------------
TODO 增加注释 增加英文注释

维护工作：

 - 主线程与调用逻辑，吕尚青，张天翊
 - 
 - 生成log部分，吕尚青
 - 
 - 压缩打包/追加文字与附件，张天翊
 - 
 - 监控log部分，吕尚青
 - 
 - 发送log部分，email与适配windows调试优化 雷言理
 - 
 - 转化为pip格式等 雷言理
 - 
 - 早期版本的email使用逻辑设计工作 吴雨卓
-------------------------------------------------------------------------------
# Project Honor list

吕尚青

张天翊

雷言理
