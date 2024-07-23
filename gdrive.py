# pylint: disable= C0116,C0114,C0115, E1101
from pathlib import Path
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account


class Gdrive:
    """Google drive handler"""

    def __init__(self, serv_account, scopes):
        self.creds = service_account.Credentials.from_service_account_file(
            serv_account, scopes=scopes
        )
        self.service = build("drive", "v3", credentials=self.creds)
        print("Google drive handler created")

    def upload_file(self, parent_folder_id, folder_name, file_name):
        # Create a MediaFileUpload object for the file
        media = MediaFileUpload(folder_name, mimetype="application/pdf", resumable=True)

        # Metadata for the file (name, mimeType, etc.)
        file_metadata = {
            "name": file_name,  # Name of the file in Google Drive
            "mimeType": "application/pdf",
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
