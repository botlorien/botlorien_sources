import os
import json
import logging
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from datetime import datetime


class Gdrive:

    def __init__(self):
        # Initialize the Drive v3 API
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.service = self._service_account_login()

    class TimeoutException(Exception):
        pass

    def time_out(void=None, time_out: int = 20, raise_exception: bool = True):
        """
        Decorator that makes a function repeat its execution until a given timeout limit
        is reached, if necessary. If the function runs without raising exceptions before
        the timeout, it is not repeated.

        :param time_out: Time limit until the function is stopped, defaults to 20
        :type time_out: int, optional
        :param raise_exception: Whether to raise an exception after timeout, defaults to False
        :type raise_exception: bool, optional
        """

        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                contador_time_out = 0
                ret = False
                error = None
                while contador_time_out < time_out:
                    try:
                        ret = func(*args, **kwargs)
                        break
                    except Exception as e:
                        error = e
                        logging.exception(error)
                        time.sleep(1)
                    contador_time_out += 1

                    if contador_time_out >= time_out and raise_exception:
                        raise error
                return ret

            return inner_wrapper

        return wrapper

    @time_out()
    def _service_account_login(self):
        """Get a service that communicates to a Google API."""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('drive.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        return service

    @time_out(time_out=3)
    def create_folder(self, folder_name):
        """Create a folder in Google Drive and return its ID."""

        # Metadata for the folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        # print(f"Folder '{folder_name}' created. ID: {folder_id}")
        return folder_id

    @time_out(time_out=3)
    def folder_exists(self, folder_name):
        """Check if a folder with the given name exists in Google Drive. Return its ID if it does, else return None."""

        # Search for folders with the specified name
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])

        # Return the ID of the first folder found (if any)
        if folders:
            # print(f"Folder '{folder_name}' already exists. ID: {folders[0]['id']}")
            return folders[0]['id']
        return None

    def create_folder_if_not_exists(self, folder_name):
        """Create a folder in Google Drive if it doesn't already exist. Return its ID."""
        existing_folder_id = self.folder_exists(folder_name)
        if existing_folder_id:
            return existing_folder_id
        else:
            return self.create_folder(folder_name)

    @time_out(time_out=3)
    def get_shareable_link(self, file_id):
        """
        Make the file publicly viewable and return its link
        """
        # Make the file viewable by 'anyone with the link'
        self.service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()

        link_shareable = f"https://drive.google.com/uc?id={file_id}"
        link_direct_download = f"https://drive.google.com/uc?export=download&id={file_id}"

        return link_direct_download

    @time_out(time_out=3)
    def delete_file(self, file_id):
        """
        Delete the file from Google Drive
        """
        self.service.files().delete(fileId=file_id).execute()
        print(f"Deleted file with ID: {file_id}")

    def delete_all_files_and_folders(self):
        """Delete all files and folders in Google Drive."""
        while self.list_all_files():
            [self.delete_file(item['id']) for item in self.list_all_files()]
        print(f"All files deleted...")

    @time_out(time_out=3)
    def list_all_files(self):
        """List all files and folders in Google Drive."""
        results = self.service.files().list().execute()
        items = results.get('files', [])
        return items

    @time_out(time_out=3,raise_exception=False)
    def upload_to_drive(self, filename, folder_name=None):
        file_metadata = {'name': os.path.basename(filename)}
        # If a folder_id is provided, set it as the parent folder for the uploaded file.
        if folder_name:
            folder_id = self.create_folder_if_not_exists(folder_name)
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(filename, mimetype='application/pdf')

        try:
            file_ = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file_.get('id')
            # print(f'File ID: {file_id}')

            # Get shareable link
            link = self.get_shareable_link(file_id)
            print(f'Shareable link: {link}')

            return link
        except HttpError as error:
            print(f'An error occurred: {error}')

    @time_out(time_out=3)
    def file_exists_in_folder(self, file_name, folder_id=None):
        """Check if a file with the given name exists in the specified folder. Return its ID if it does, else return None."""

        # Search for files with the specified name in the given folder
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        # Return the ID of the first file found (if any)
        if files:
            # print(f"File '{file_name}' already exists in folder ID: {folder_id}. File ID: {files[0]['id']}")
            return files[0]['id']
        return None

    def upload_file_if_not_exists(self, file_path, folder_name):
        file_name = os.path.basename(file_path)

        folder_id = self.create_folder_if_not_exists(folder_name) if folder_name else None

        existing_file_id = self.file_exists_in_folder(file_name, folder_id)
        if existing_file_id:
            return existing_file_id
        else:
            return self.upload_to_drive(file_path, folder_name)


if __name__ == '__main__':
    pass