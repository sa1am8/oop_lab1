from render import SpreadsheetApp
from google_drive import driver
from file import FileManager
from settings import get_settings, Settings


settings: Settings = get_settings()
app = SpreadsheetApp()


if __name__ == "__main__":
    # = [C0:R3] + (123 * 1  - (12 / 2 - 1)) - syntax

    sheet_data = driver.read_file(settings.FILE_ID)
    FileManager.load_file(sheet_data, app.cells)

    app.refresh_values(app.cells)
    app.mainloop()
