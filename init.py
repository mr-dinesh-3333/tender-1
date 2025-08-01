import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import os
import logging


def send_email(subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = sender  # Or use separate receiver

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Email failed: {e}")


def send_whatsapp_alert(message):
    try:
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
        message = client.messages.create(
            body=message,
            from_="whatsapp:+14155238886",
            to="whatsapp:" + os.getenv("RECIPIENT_NUMBER", "+917386531980")
        )
        logging.info(f"WhatsApp alert sent: {message.sid}")
    except Exception as e:
        logging.error(f"WhatsApp failed: {e}")