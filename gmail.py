from __future__ import print_function
import os.path
import base64
import json
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Create the email
        message = create_message(
            "your_email@gmail.com",
            "recipient_email@gmail.com",
            "Subject of the email",
            "Body of the email",
        )
        send_message(service, "me", message)
        print("Email sent successfully!")

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_message(sender, to, subject, body):
    """Create a message for an email."""
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    msg = MIMEText(body)
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_message(service, sender, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=sender, body=message).execute()
        print(f'Sent message to {sender} Message Id: {message["id"]}')
        return message
    except Exception as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
