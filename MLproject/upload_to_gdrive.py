# upload_to_drive.py
import os
import sys
import pathlib
import logging
from google.oauth2 import service_account
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Ingat: "mlruns" adalah folder default hasil mlflow local run.
# Parameter:
#   - local_folder   = folder local yang akan diupload
#   - drive_folder_id = ID folder di Google Drive
#   Contoh pemanggilan:
#   python upload_to_drive.py ./mlruns <GOOGLE_DRIVE_FOLDER_ID>

def upload_folder_to_gdrive(local_folder: str, drive_folder_id: str):
    # Pastikan foldernya ada
    local_folder_path = pathlib.Path(local_folder)
    if not local_folder_path.exists():
        logging.error(f"Folder '{local_folder}' tidak ditemukan.")
        return

    # 1. Buat sementara file 'service_account.json' dari environment variable
    service_account_file = "service_account.json"
    with open(service_account_file, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    # 2. Load credential service account dengan scope Drive
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)

    # 3. Auth dengan PyDrive2
    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)

    # 4. Rekursif upload seluruh isi folder
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            file_path = pathlib.Path(root) / filename
            rel_path = file_path.relative_to(local_folder_path)

            # Buat file di Google Drive, simpan ke folder drive_folder_id
            gfile = drive.CreateFile({
                "title": str(rel_path),    # nama file di Drive
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(str(file_path))
            gfile.Upload()
            logging.info(f"Uploaded: {rel_path} -> Drive folder {drive_folder_id}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python upload_to_drive.py <local_folder> <drive_folder_id>")
        sys.exit(1)
    local_folder = sys.argv[1]
    drive_folder_id = sys.argv[2]

    upload_folder_to_gdrive(local_folder, drive_folder_id)

if __name__ == "__main__":
    main()