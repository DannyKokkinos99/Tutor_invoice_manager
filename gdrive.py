# pylint: disable= C0116,C0114,C0115, E1101
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import io
import re


class Gdrive:
    """Google drive handler"""

    def __init__(self, serv_account, scopes):
        self.creds = service_account.Credentials.from_service_account_file(
            serv_account, scopes=scopes
        )
        self.service = build("drive", "v3", credentials=self.creds)
        self.docs_service = build("docs", "v1", credentials=self.creds)
        print("Google drive handler created")

    def upload_file(
        self, parent_folder_id, folder_name, file_name, mimetype="application/pdf"
    ):
        # Create a MediaFileUpload object for the file
        media = MediaFileUpload(folder_name, mimetype=mimetype, resumable=True)

        # Metadata for the file (name, mimeType, etc.)
        file_metadata = {
            "name": file_name,  # Name of the file in Google Drive
            "mimeType": mimetype,
            "parents": [parent_folder_id],  # ID of the folder to upload the file to
        }

        # Upload the file to Google Drive
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"File uploaded: {file}")

    def print_about(self):
        about = self.service.about().get(fields="user").execute()
        user_info = about.get("user", {})
        print(
            f"Authenticated as: {user_info.get('displayName')} ({user_info.get('emailAddress')})"
        )

    def list_files(self, folder_id=None):
        # Call the Drive v3 API
        query = f"'{folder_id}' in parents" if folder_id else None
        results = (
            self.service.files()
            .list(q=query, pageSize=100, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
        else:
            print("Files:")
            for item in items:
                print(f'{item["name"]} ({item["id"]})')

    def file_count(self, folder_id):
        query = f"'{folder_id}' in parents" if folder_id else None
        results = (
            self.service.files()
            .list(q=query, pageSize=100, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        num_items = len(items)
        print(f"{num_items} found in folder {folder_id}")
        return num_items

    def folder_exists(self, parent_folder_id, folder_name):
        # Properly format the query to avoid invalid characters
        query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"

        try:
            # Call the Drive API to check if the folder exists
            results = (
                self.service.files().list(q=query, fields="files(id, name)").execute()
            )
            items = results.get("files", [])

            if items:
                # Folder found
                return items[0]["id"]
            else:
                # Folder not found
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def create_folder(self, parent_folder_id, folder_name):
        # Metadata for the new folder
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        }

        # Create the folder
        folder = (
            self.service.files().create(body=folder_metadata, fields="id").execute()
        )
        print(f'Created folder: {folder_name} with ID: {folder.get("id")}')
        return folder.get("id")

    def ensure_folder_exists(self, parent_folder_id, folder_name):
        print(f"Checking if {folder_name} folder exists")
        folder_id = self.folder_exists(parent_folder_id, folder_name)
        if folder_id:
            print(f'Folder "{folder_name}" already exists with ID: {folder_id}')
            return folder_id
        else:
            return self.create_folder(parent_folder_id, folder_name)

    def update_database(self, parent_folder_id, parent_path):
        query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])
        folder_names = [folder["name"] for folder in folders]
        folder_ids = [folder["id"] for folder in folders]
        for folder_name, folder_id in zip(folder_names, folder_ids):
            folder_path = os.path.join(parent_path, folder_name)
            self.download_folder(folder_id, folder_path)
        return folder_names

    def download_folder(self, folder_id, local_path):

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        # Query to get all files within the specified folder
        query = f"'{folder_id}' in parents"
        results = (
            self.service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        items = results.get("files", [])

        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            file_path = os.path.join(local_path, file_name)

            # Check if it's a folder or a file
            if item["mimeType"] == "application/vnd.google-apps.folder":
                # Recursively download subfolder
                self.download_folder(file_id, file_path)
            else:
                # Download the file
                request = self.service.files().get_media(fileId=file_id)
                file_data = io.BytesIO()
                downloader = MediaIoBaseDownload(file_data, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {file_name}: {int(status.progress() * 100)}%.")

                # Write the downloaded content to the local file
                with open(file_path, "wb") as f:
                    file_data.seek(0)
                    f.write(file_data.read())

                print(f"File {file_name} downloaded successfully.")

    def get_students_from_gdoc(self, document_id):
        """Reads the content of a Google Doc and parses student information."""

        # Retrieve the document content from Google Docs API
        document = self.docs_service.documents().get(documentId=document_id).execute()

        # Extract the full text from the document
        full_text = ""
        for element in document.get("body").get("content"):
            if "paragraph" in element:
                paragraph = element["paragraph"]
                for text_run in paragraph.get("elements", []):
                    if "textRun" in text_run:
                        full_text += text_run["textRun"]["content"]

        # Split the text into student blocks based on double newlines
        student_blocks = re.split(r"\n\s*\n", full_text.strip())

        # Parse each student block
        students = []
        for block in student_blocks:
            lines = block.splitlines()
            if (
                len(lines) >= 8
            ):  # Ensure there are enough lines to form a student record
                student = {
                    "name": lines[0].strip(),
                    "surname": lines[1].strip(),
                    "parent": lines[2].strip(),
                    "email": lines[3].strip(),
                    "address": lines[4].strip(),
                    "phone_number": lines[5].strip(),
                    "price_per_hour": lines[6].strip(),
                    "invoice_count": lines[7].strip(),
                }
                students.append(student)

        return students
