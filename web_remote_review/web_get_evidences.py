import sys, os, io
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from Google import Create_Service

# Connection with Google Cloud using Auth2.0
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
folder_id = '18aJTxbazV-zxcygJQ4E9qIu1f1bwAAWH'

download_list = sys.argv[1]
source = download_list.split(",")

dir = './web_evidence'
dont_remove = '.gitignore'
for f in os.listdir(dir):
    if f != dont_remove:
        os.remove(os.path.join(dir, f))
        
mystring = ".jpg"
file_names = [s + mystring for s in source]

for file_id, file_name in zip(source, file_names):
    request = service.files().get_media(fileId=file_id)
    
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    
    while not done:
        status, done = downloader.next_chunk()
        # print('Download progress {0}'.format(status.progress()*100))
        
    fh.seek(0)
    with open(os.path.join('./web_evidence', file_name), 'wb') as f:
        f.write(fh.read())
        f.close()