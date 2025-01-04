# upload_to_drive.py
import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_folder(local_folder, drive_folder_id):
    # 1. Buat file `service_account.json` dari environment variable
    service_account_json_path = "service_account.json"
    with open(service_account_json_path, "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    # 2. Inisialisasi GoogleAuth
    gauth = GoogleAuth()

    # 3. Setel setting untuk service account
    #    (Tidak perlu memanggil .LoadServiceConfig(), karena tidak ada di PyDrive2)
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = {
        "client_json_file_path": service_account_json_path
    }

    # 4. ServiceAuth untuk autentikasi
    gauth.ServiceAuth()

    drive = GoogleDrive(gauth)

    # 5. Upload semua file di local_folder ke drive_folder_id
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Path relatif untuk penamaan di GDrive (jika ingin struktur folder asli)
            rel_path = os.path.relpath(file_path, local_folder)

            gfile = drive.CreateFile({
                "title": rel_path,
                "parents": [{"id": drive_folder_id}]
            })
            gfile.SetContentFile(file_path)
            gfile.Upload()

if __name__ == "__main__":
    import sys
    local_folder = sys.argv[1]      # misal "./mlruns"
    drive_folder_id = sys.argv[2]  # ID folder di GDrive
    upload_folder(local_folder, drive_folder_id)
