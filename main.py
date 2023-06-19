import sys
import glob
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from colorama import init, Fore, Style

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file']

# Initialize colorama for Windows environment
init()


def cprint(s, color=Fore.BLUE, brightness=Style.NORMAL, **kwargs):
    """Utility function wrapping the regular `print()` function
    but with colors and brightness."""
    print(f"{brightness}{color}{s}{Style.RESET_ALL}", **kwargs)


def get_gdrive_service():
    """Returns the Google Drive API service using OAuth 2.0 credentials."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('.Creds/token.pickle'):
        with open('.Creds/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.Creds/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('.Creds/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # Return Google Drive API service
    return build('drive', 'v3', credentials=creds)


def upload_files(path, folder):
    """Uploads files from a given path to Google Drive within a specified folder."""

    def process_files_with_extension(extension):
        """Processes files with the specified extension and uploads them to Google Drive."""
        files = glob.glob1(path, "*" + extension)
        total = len(files)
        cprint("Total " + extension[1:] + " files: ", total)

        for i, file_name in enumerate(files):
            # Define file metadata, such as the name and the parent folder ID
            file_metadata = {
                "name": file_name,
                "parents": [folder_id]
            }
            cprint("\nUploading ", file_name, " to Google Drive.")
            media = MediaFileUpload(os.path.join(path, file_name), resumable=True)
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            cprint("File created, id:", uploaded_file.get("id"))
            cprint("Uploaded ", i + 1, "/", total)

    # Authenticate the Google Drive account
    service = get_gdrive_service()

    # Define the folder details we want to create
    folder_metadata = {
        "name": folder,
        "mimeType": "application/vnd.google-apps.folder"
    }

    # Create the folder
    created_folder = service.files().create(body=folder_metadata, fields="id").execute()

    # Get the folder id
    folder_id = created_folder.get("id")
    cprint("Folder ID:", folder_id)

    # Upload files with specific extensions
    files_extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.mkv']
    for extension in files_extensions:
        process_files_with_extension(extension)


def main():
    """Main function that prompts the user for input and initiates file uploading."""

    # Input directory
    path = input('Enter the path to the folder: ')

    if os.path.isdir(path):
        # Output directory
        folder = input("\nWhat do you want to call the folder: ")
        upload_files(path, folder)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
