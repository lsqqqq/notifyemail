# 如何使用SMTP

SMTP（Simple Mail Transfer Protocol）即简单邮件传输协议,它是一组用于由源地址到目的地址传送邮件的规则，由它来控制信件的中转方式。
在python中，我们使用email构造邮件，使用smtplib库来发送电子邮件
使用方法示例：
```python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
```

## 第三方 SMTP 服务
```bash
mail_host = "smtp.qq.com"  # 设置服务器
mail_user = "******@qq.com"  # 用户名
mail_pass = "xxxxxxxxxxxxx"  # 授权码
sender = '******@qq.com'
receivers = ['****@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
message['From'] = Header("Python SMTP教程", 'utf-8') #括号里的对应发件人邮箱昵称（随便起）、发件人邮箱账号
message['To'] = Header("测试", 'utf-8') #括号里的对应收件人邮箱昵称、收件人邮箱账号
subject = 'Python SMTP 邮件测试'
message['Subject'] = Header(subject, 'utf-8')
try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 465)  # 发件人邮箱中的SMTP服务器，端口是465
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")

```

## 常用邮箱的smtp服务器地址

- 新浪邮箱：smtp.sina.com,
- 新浪VIP：smtp.vip.sina.com,
- 搜狐邮箱：http://smtp.sohu.com，
- 126邮箱：smtp.126.com,
- 139邮箱：smtp.139.com,
- 163网易邮箱：http://smtp.163.com.

注意授权码只会显示一次！请一定记得复制！