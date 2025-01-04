# upload_to_drive.py
import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def main(local_folder, drive_folder_id):
    # Buat file credentials.json dari environment variable
    creds_file = "service_account_credentials.json"
    with open(creds_file, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    # Inisialisasi GoogleAuth
    gauth = GoogleAuth()
    gauth.service_config = {
        "client_config_backend": "service",
        "service_config": creds_file
    }
    gauth.LoadServiceConfig()
    gauth.Authorize()

    drive = GoogleDrive(gauth)

    # Upload isi folder local_folder ke Drive
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Path relatif untuk penamaan di GDrive (jika perlu)
            rel_path = os.path.relpath(file_path, local_folder)
            
            gfile = drive.CreateFile({
                "title": rel_path,  
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(file_path)
            gfile.Upload()

if __name__ == "__main__":
    
    import sys
    local_folder = sys.argv[1]  # e.g. "./mlruns"
    drive_folder_id = sys.argv[2]  # folder ID di GDrive
    main(local_folder, drive_folder_id)
