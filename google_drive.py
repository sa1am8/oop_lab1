import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleDriveManager:
    def __init__(self):
        self.credentials = None

        if os.path.exists("token.json"):
            self.credentials = Credentials.from_authorized_user_file(
                "token.json", SCOPES
            )

        if not self.credentials or not self.credentials.valid:
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(self.credentials.to_json())

        self.service = build("sheets", "v4", credentials=self.credentials)

    def download_file(self, file_id):
        request = self.service.files().get_media(fileId=file_id)
        downloaded_file = BytesIO()
        downloader = MediaIoBaseDownload(downloaded_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        downloaded_file.seek(0)
        return downloaded_file

    def save_sheet(self, file_id: str, body: dict):
        resp = (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=file_id,
                range="Аркуш1!A1",
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return resp

    def read_file(self, file_id: str):
        return (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=file_id, range="Аркуш1!A1:Z10")
            .execute()
        )


driver = GoogleDriveManager()
