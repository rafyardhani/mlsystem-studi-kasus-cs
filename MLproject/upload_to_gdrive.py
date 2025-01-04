import os
import sys
import pathlib
import logging

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def main(local_folder: str, drive_folder_id: str):
    # 1. Tulis file service_account.json dari ENV: GDRIVE_CREDENTIALS
    service_account_file = "service_account.json"
    with open(service_account_file, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])  # Pastikan secret sudah disiapkan

    # 2. Konfigurasi PyDrive2 (service account)
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    # Pastikan "client_user_email" tidak diisi jika TIDAK perlu domain-wide delegation
    gauth.settings["service_config"] = {
        "client_json_file_path": service_account_file
    }

    # 3. Autentikasi
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)

    # 4. Pastikan folder lokal ada
    folder_path = pathlib.Path(local_folder)
    if not folder_path.exists():
        logging.error(f"Folder '{local_folder}' tidak ditemukan!")
        sys.exit(1)

    # 5. Rekursif upload isi folder local_folder
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = pathlib.Path(root) / filename
            # Buat path relatif untuk penamaan file di Drive
            rel_path = file_path.relative_to(folder_path)

            # Buat file di GDrive
            gfile = drive.CreateFile({
                "title": str(rel_path),
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(str(file_path))
            gfile.Upload()

            logging.info(f"Uploaded: {rel_path} -> Drive folder {drive_folder_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_drive.py <local_folder> <drive_folder_id>")
        sys.exit(1)
    local_folder_arg = sys.argv[1]
    drive_folder_id_arg = sys.argv[2]
    main(local_folder_arg, drive_folder_id_arg)