# pylint: disable= C0116,C0114,C0115
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utility.logger import logger


class Emailer:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, content, recipient):

        try:
            # Establish a secure session with Outlook's outgoing SMTP server

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            today = datetime.today()
            formatted_date = str(today.strftime("%d-%m-%Y"))

            with open(content, encoding="UTF-8") as file:
                body = file.read()
            subject = f"Maths tutoring invoice - {formatted_date}"

            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient.email
            body = body.replace("[PARENT]", recipient.parent)

            # Attach the message body
            msg.attach(MIMEText(body, "plain"))

            # Attach a file
            invoice_name = f"Invoice-{recipient.invoice_count}.pdf"
            filename = f"Invoices/{recipient.name}/{invoice_name}"
            attachment = open(filename, "rb")
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename= {invoice_name}"
            )
            msg.attach(part)

            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient.email, text)
            logger.info("Email sent ✅")

            # Terminate the SMTP session and close the connection
            server.quit()

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Email failed to send! {e}")
            server.quit()
