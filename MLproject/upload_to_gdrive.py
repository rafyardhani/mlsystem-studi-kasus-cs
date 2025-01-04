import os
import sys
import pathlib
import logging

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def main(local_folder: str, drive_folder_id: str):
    # Tulis file service_account.json dari env
    service_account_file = "service_account.json"
    with open(service_account_file, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    # TANPA client_user_email
    gauth.settings["service_config"] = {
        "client_json_file_path": service_account_file
    }

    # Autentikasi service account (bukan domain-wide delegation)
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)

    # Upload folder local_folder
    folder_path = pathlib.Path(local_folder)
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
            logging.info(f"Uploaded {rel_path} -> folder {drive_folder_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_drive.py <local_folder> <drive_folder_id>")
        sys.exit(1)

    local_folder_arg = sys.argv[1]
    drive_folder_id_arg = sys.argv[2]
    main(local_folder_arg, drive_folder_id_arg)
