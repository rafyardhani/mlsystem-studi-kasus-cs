from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import pathlib
import sys

def main(local_folder: str, drive_folder_id: str):
    # 1. Tulis service account file
    with open("service_account.json", "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(
        "MLproject/service_account.json", scopes=SCOPES
    )

    # 2. Bungkus jadi AuthorizedHttp
    auth_http = AuthorizedHttp(creds)

    # 3. Inject ke PyDrive2
    gauth = GoogleAuth()
    gauth.http = auth_http
    drive = GoogleDrive(gauth)

    # 4. Upload isi folder
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload.py <local_folder> <drive_folder_id>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
