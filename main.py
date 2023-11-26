from render import SpreadsheetApp
from google_drive import GoogleDriveManager
from file import FileManager

app = SpreadsheetApp()
google_sheets = GoogleDriveManager()
file = FileManager()

if __name__ == "__main__":
    # service = authenticate_google_drive_api()
    # google_drive_manager = GoogleDriveManager(service)
    # = [C0:R3] + (123 * 1  - (12 / 2 - 1)) - syntax

    sheet_data = google_sheets.read_file("1YkRyeLTtAfJ5DSmLDcYxJ8rMGZhz8kYH1yxb5eE3OvY")
    file.load_file(sheet_data, app.cells)

    app.refresh_values(app.cells)
    
    app.mainloop()
