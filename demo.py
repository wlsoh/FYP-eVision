import os
import io
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from Google import Create_Service
import pandas as pd

CLIENT_SECRET_FILE = 'Client_Secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
folder_id = '18aJTxbazV-zxcygJQ4E9qIu1f1bwAAWH'

# Upload a file to folder
# file_names = ['9 - Edit Password - Both.png']
# mime_types = ['image/jpg']

# for file_name, mime_type in zip(file_names, mime_types):
#     file_metadata = {
#         'name': file_name,
#         'parents': [folder_id]
#     }

#     media = MediaFileUpload('./temp/{0}'.format(file_name), mimetype=mime_type)
    
#     service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id'
#     ).execute()
    
    
# Get list of file
# query = f"parents = '{folder_id}'"
# response = service.files().list(q=query).execute()
# files = response.get('files')
# nextPageToken = response.get('nextPageToken')

# while nextPageToken:
#     response = service.files().list(q=query, pageToken=nextPageToken).execute()
#     files.extend(response.get('files'))
#     nextPageToken = response.get('nextPageToken')
    
# pd.set_option('display.max_columns', 100)
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.min_rows', 500)
# pd.set_option('display.max_colwidth', 150)
# pd.set_option('display.width', 200)
# pd.set_option('expand_frame_repr', True)
# df = pd.DataFrame(files)
# print(df)


# Download the uploaded file
file_ids = ['1tPLVCcLDVOQMfhXCAZAFF9Q42CYKNvpz']
file_names = ['test.jpg']

for file_id, file_name in zip(file_ids, file_names):
    request = service.files().get_media(fileId=file_id)
    
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    
    while not done:
        status, done = downloader.next_chunk()
        print('Download progress {0}'.format(status.progress()*100))
        
    fh.seek(0)
    with open(os.path.join('./temp', file_name), 'wb') as f:
        f.write(fh.read())
        f.close()