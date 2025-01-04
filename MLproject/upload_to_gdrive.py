import os
import sys
import json
import pathlib
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def main(local_folder: str, drive_folder_id: str):
    # 1. Baca isi JSON service account dari environment variable (GDRIVE_CREDENTIALS)
    creds_json = os.environ.get("GDRIVE_CREDENTIALS")
    if not creds_json:
        print("Error: GDRIVE_CREDENTIALS environment variable is empty or not set.")
        sys.exit(1)

    # Ubah string JSON menjadi dictionary
    creds_dict = json.loads(creds_json)

    # 2. Inisialisasi credentials dari dictionary (bukan dari file)
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )

    # 3. Bungkus credentials dengan AuthorizedHttp
    auth_http = AuthorizedHttp(creds)

    # 4. Inject ke PyDrive2
    gauth = GoogleAuth()
    gauth.http = auth_http
    drive = GoogleDrive(gauth)

    # 5. Upload isi folder local_folder ke Google Drive
    folder_path = pathlib.Path(local_folder)
    if not folder_path.exists():
        print(f"Error: Folder '{local_folder}' tidak ditemukan.")
        sys.exit(1)

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = pathlib.Path(root) / filename
            rel_path = file_path.relative_to(folder_path)

            gfile = drive.CreateFile({
                "title": str(rel_path),
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(str(file_path))
            gfile.Upload()
            print(f"Uploaded: {rel_path} -> Drive folder {drive_folder_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload.py <local_folder> <drive_folder_id>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])