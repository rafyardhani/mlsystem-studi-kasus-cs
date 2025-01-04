# upload_to_drive.py
import os
import sys
import pathlib
import logging

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def main(local_folder: str, drive_folder_id: str):
    # Pastikan folder lokal ada
    local_folder_path = pathlib.Path(local_folder)
    if not local_folder_path.exists():
        logging.error(f"Folder '{local_folder}' tidak ditemukan!")
        sys.exit(1)

    # 1. Buat file 'service_account.json' dari ENV: GDRIVE_CREDENTIALS
    service_account_file = "service_account.json"
    with open(service_account_file, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    # 2. Konfigurasikan PyDrive2 untuk service account
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = {
        "client_json_file_path": service_account_file
        # Jika Anda butuh domain-wide delegation, tambahkan:
        # "client_user_email": "user@domain.com"
    }

    # 3. Otorisasi dengan service account
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)

    # 4. Upload isi folder local_folder ke folder di GDrive
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            file_path = pathlib.Path(root) / filename
            # buat path relatif agar struktur di GDrive lebih jelas (opsional)
            rel_path = file_path.relative_to(local_folder_path)

            # Buat file di GDrive
            gfile = drive.CreateFile({
                "title": str(rel_path),
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(str(file_path))
            gfile.Upload()
            logging.info(f"Uploaded {rel_path} -> Drive folder {drive_folder_id}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_drive.py <local_folder> <drive_folder_id>")
        sys.exit(1)

    local_folder_arg = sys.argv[1]
    drive_folder_id_arg = sys.argv[2]
    main(local_folder_arg, drive_folder_id_arg)