# upload_to_drive.py

import os
import sys
import json
import pathlib
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp

def main(local_folder: str, drive_folder_id: str):
    creds_json = os.environ.get("GDRIVE_CREDENTIALS")
    if not creds_json:
        print("Error: GDRIVE_CREDENTIALS is not set or empty.")
        sys.exit(1)

    # Tulis sementara ke 'service_account.json'
    with open("service_account.json", "w") as f:
        f.write(creds_json)

    # Atur PyDrive2 untuk "service" backend
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = {
        "client_json_file_path": "service_account.json"
    }
    # Lalu panggil ServiceAuth
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)

    # 6) Upload semua isi folder local_folder ke drive_folder_id
    folder_path = pathlib.Path(local_folder)
    if not folder_path.exists():
        print(f"Error: Folder '{local_folder}' not found.")
        sys.exit(1)

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = pathlib.Path(root) / filename
            rel_path = file_path.relative_to(folder_path)

            # Buat file di GDrive
            gfile = drive.CreateFile({
                "title": str(rel_path),  # Nama file di GDrive
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(str(file_path))
            gfile.Upload()
            print(f"Uploaded {rel_path} to folder {drive_folder_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_drive.py <local_folder> <drive_folder_id>")
        sys.exit(1)

    local_folder_arg = sys.argv[1]
    drive_folder_id_arg = sys.argv[2]

    main(local_folder_arg, drive_folder_id_arg)