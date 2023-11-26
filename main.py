from render import SpreadsheetApp
from google_drive import driver
from file import FileManager

app = SpreadsheetApp()

FILE_ID = "1ozWMQ1y7YzvDUNGxPbjRAx-c-TyV0SQT1cVk53k0_y4"

if __name__ == "__main__":
    # = [C0:R3] + (123 * 1  - (12 / 2 - 1)) - syntax

    sheet_data = driver.read_file(FILE_ID)
    FileManager.load_file(sheet_data, app.cells)

    app.refresh_values(app.cells)
    app.mainloop()
