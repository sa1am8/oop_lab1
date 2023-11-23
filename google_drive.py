# from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO


class GoogleDriveManager:
    def __init__(self, service):
        self.service = service

    def download_file(self, file_id):
        request = self.service.files().get_media(fileId=file_id)
        downloaded_file = BytesIO()
        downloader = MediaIoBaseDownload(downloaded_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        downloaded_file.seek(0)
        return downloaded_file

    def save_file_to_google_drive(self, file_name, file_data):
        # Ваш код для збереження файлу на Google Drive тут
        pass

    def get_files_from_google_drive(self):
        # Ваш код для отримання файлів з Google Drive тут
        pass
