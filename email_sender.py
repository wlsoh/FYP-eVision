#wrprqrkahnxqgjma
import smtplib
from email.message import EmailMessage

def mail_resetpass(receiverlist, temppass):
    global success
    email_address = "evisionmalaysia@gmail.com"
    email_password = "wrprqrkahnxqgjma"
    contacts = receiverlist
    success = False
    
    content = "Hi,\n\nYour password had been successfully reset. You may use the following generated temporary password to login.\n\nTemporary Password: {}\n\nHave a good day,\ne-Vision Support Team\n\nThis email was generated by computer. Please do not reply.".format(temppass)

    msg = EmailMessage()
    msg['Subject'] = "Reset Password"
    msg['From'] = email_address
    msg['To'] = ', '.join(contacts)
    msg.set_content(content, subtype="plain", charset='us-ascii')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        
        smtp.login(email_address, email_password)
        
        try:
            smtp.send_message(msg)
            success = True
        except smtplib.SMTPException:
            success = False
            print("Error: an error occured in SMTP server. Failed to send email")
        
        return success
    
def mail_newuserregister(receiverlist, temppass):
    global success
    email_address = "evisionmalaysia@gmail.com"
    email_password = "wrprqrkahnxqgjma"
    contacts = receiverlist
    success = False
    
    content = "Hi,\n\nWelcome to e-Vision. An account had been successfully created by company's Admin for you. Please use the following details to login to the system.\n\nEmail Address: {}\nTemporary Password: {}\n\nHave a good day,\ne-Vision Support Team\n\nThis email was generated by computer. Please do not reply.".format(contacts[0], temppass)

    msg = EmailMessage()
    msg['Subject'] = "e-Vision Account Created"
    msg['From'] = email_address
    msg['To'] = ', '.join(contacts)
    msg.set_content(content, subtype="plain", charset='us-ascii')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        
        smtp.login(email_address, email_password)
        
        try:
            smtp.send_message(msg)
            success = True
        except smtplib.SMTPException:
            success = False
            print("Error: an error occured in SMTP server. Failed to send email")
        
        return success