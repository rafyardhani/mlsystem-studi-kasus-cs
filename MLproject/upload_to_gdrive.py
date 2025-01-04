import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --------------------------------------------------------------------
# 1. Load credential service account
# --------------------------------------------------------------------
creds = json.loads(os.environ["GDRIVE_CREDENTIALS"])
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# Build Drive API
service = build('drive', 'v3', credentials=credentials)

# --------------------------------------------------------------------
# 2. Buat folder "mlruns" di Shared Drive
#    Pastikan SHARED_DRIVE_ID adalah ID root Shared Drive (atau folder 
#    di Shared Drive) yang bisa diakses oleh service account Anda.
# --------------------------------------------------------------------
SHARED_DRIVE_ID = "1f5ecMJvCs6jYT2kkeNn0zoZ9xyXAWFRC"

folder_metadata = {
    'name': 'mlruns',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [SHARED_DRIVE_ID]  # Jika ini ID root Shared Drive -> folder "mlruns" muncul di root
}

mlruns_folder = service.files().create(
    body=folder_metadata,
    fields='id',
    supportsAllDrives=True
).execute()
mlruns_folder_id = mlruns_folder.get('id')
print(f"Folder 'mlruns' created in Shared Drive with ID: {mlruns_folder_id}")


# --------------------------------------------------------------------
# 3. Fungsi rekursif untuk membuat folder dan upload file
#    Menjaga struktur subfolder sesuai di lokal
# --------------------------------------------------------------------
def upload_directory(local_dir_path, parent_drive_id):
    """
    Melakukan:
      - Cek item di local_dir_path,
      - Jika folder -> buat folder di Drive (dengan parent_drive_id), 
                      lalu rekursif ke dalamnya,
      - Jika file   -> upload file ke Drive (parent_drive_id).
    """
    for item_name in os.listdir(local_dir_path):
        local_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(local_path):
            # Buat folder di Drive
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()

            new_folder_id = created_folder.get('id')
            print(f"Created folder: {item_name} (ID: {new_folder_id})")

            # Rekursif ke subfolder
            upload_directory(local_path, new_folder_id)
        else:
            # Upload file
            print(f"Uploading file: {item_name}")
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(local_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()


# --------------------------------------------------------------------
# 4. Mulai upload dari 'run_id' yang ada di dalam "./mlruns/0"
#    Sehingga folder '0' di lokal TIDAK terbawa ke Drive.
# --------------------------------------------------------------------
local_mlruns_0 = './mlruns/0'

# Di dalam './mlruns/0', biasanya ada subfolder = <run_id_1>, <run_id_2>, dsb.
# Kita akan membuat subfolder <run_id_x> langsung di bawah folder "mlruns" di Drive.
for run_id_name in os.listdir(local_mlruns_0):
    run_id_local_path = os.path.join(local_mlruns_0, run_id_name)
    
    # Pastikan ini adalah folder, bukan file
    if os.path.isdir(run_id_local_path):
        # Buat folder <run_id_name> di dalam "mlruns"
        run_id_folder_meta = {
            'name': run_id_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [mlruns_folder_id]
        }
        run_id_folder = service.files().create(
            body=run_id_folder_meta,
            fields='id',
            supportsAllDrives=True
        ).execute()
        run_id_folder_id = run_id_folder.get('id')
        print(f"Created run_id folder: {run_id_name} (ID: {run_id_folder_id})")

        # Upload isinya secara rekursif
        upload_directory(run_id_local_path, run_id_folder_id)

print(f"All run_id folders and files have been uploaded to Drive!")