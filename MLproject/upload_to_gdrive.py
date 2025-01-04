import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Mengambil kredensial dari secret GitHub (gunakan format json)
creds = json.loads(os.environ["GDRIVE_CREDENTIALS"])  # Ambil JSON dari secret GitHub

# Membuat kredensial dari file JSON dan menambahkan scope
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]  # atau drive.file
)

# Membangun layanan Google Drive API
service = build('drive', 'v3', credentials=credentials)

folder_metadata = {
    'name': 'mlruns',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': '1f5ecMJvCs6jYT2kkeNn0zoZ9xyXAWFRC'  # ID dari Shared Drive
}
folder = service.files().create(
    body=folder_metadata,
    fields='id',
    supportsAllDrives=True
).execute()

# Upload file ke folder yang baru dibuat
folder_id = folder.get('id')
for root, dirs, files in os.walk('./mlruns'):
    for file_name in files:
        print(f"Uploading {file_name}...")
        file_path = os.path.join(root, file_name)
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print("Files uploaded successfully! to link: https://drive.google.com/drive/folders/" + folder_id)

