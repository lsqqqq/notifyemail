# How to Use SMTP

SMTP (Simple Mail Transfer Protocol) is a set of rules used to transmit emails from the source address to the destination address, controlling the way the mail is relayed. In Python, we can construct emails using the email module and send them using the smtplib library.

Here is an example of how to use it:

```python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
```

## Third-Party SMTP Service

To use a third-party SMTP service for sending emails, you need to provide the necessary information:
```bash
mail_host = "smtp.qq.com"       # Set the SMTP server
mail_user = "******@qq.com"    # Your username (email address)
mail_pass = "xxxxxxxxxxxxx"    # Your authorization code (password)
sender = '******@qq.com'       # Your email address
receivers = ['****@qq.com']    # The recipient's email address (can be your QQ email or other email)
message = MIMEText('Python email test...', 'plain', 'utf-8')
message['From'] = Header("Python SMTP Tutorial", 'utf-8') # The sender's name and email address
message['To'] = Header("Test", 'utf-8')  # The recipient's name and email address
subject = 'Python SMTP email test'             # The subject of the email
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 465)  # Connect to the SMTP server using the port 465 (SSL)
    smtpObj.login(mail_user, mail_pass)  # Log in using your email and authorization code
    smtpObj.sendmail(sender, receivers, message.as_string())  # Send the email
    print("Mail sent successfully")
except smtplib.SMTPException:
    print("Error: Failed to send the email")
```