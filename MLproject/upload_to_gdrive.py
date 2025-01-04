import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Load credential service account
creds = json.loads(os.environ["GDRIVE_CREDENTIALS"])
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 2. Build Drive API
service = build('drive', 'v3', credentials=credentials)

# 3. ID Shared Drive (pastikan benar, dan SA punya akses Content Manager)
SHARED_DRIVE_ID = "1f5ecMJvCs6jYT2kkeNn0zoZ9xyXAWFRC"  # Contoh, mungkin berbeda format

# 4. Buat folder "mlruns" di root Shared Drive
folder_metadata = {
    'name': 'mlruns',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [SHARED_DRIVE_ID]
}
mlruns_folder = service.files().create(
    body=folder_metadata,
    fields='id',
    supportsAllDrives=True
).execute()
mlruns_folder_id = mlruns_folder.get('id')
print(f"Folder 'mlruns' created in Shared Drive with ID: {mlruns_folder_id}")


def upload_directory(local_dir_path, parent_drive_id):
    """
    Fungsi rekursif untuk:
    - Membuat subfolder di Drive jika ketemu subfolder di lokal,
    - Mengunggah file ke folder Drive sesuai struktur lokal.
    """
    # List isi folder lokal
    for item_name in os.listdir(local_dir_path):
        item_full_path = os.path.join(local_dir_path, item_name)

        if os.path.isdir(item_full_path):
            # Buat folder dengan nama item_name di Drive
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
            print(f"Folder created: {item_name} (ID: {new_folder_id})")

            # Rekursif ke subfolder
            upload_directory(item_full_path, new_folder_id)

        else:
            # Jika item adalah file, upload ke parent_drive_id
            print(f"Uploading file: {item_name}")
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_full_path, resumable=True)

            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()


# 5. Jalankan upload directory rekursif mulai dari ./mlruns/0
local_mlruns_0_path = './mlruns/0'
upload_directory(local_mlruns_0_path, mlruns_folder_id)

print("All files & subfolders uploaded successfully!")
print("Drive link:", f"https://drive.google.com/drive/folders/{mlruns_folder_id}")