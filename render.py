import tkinter as tk
from tkinter import ttk

from settings import get_settings, Settings
from models import Cell
from expression import Expression


settings: Settings = get_settings()


class SpreadsheetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(settings.TABLE_NAME)
        self.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")

        self.cells = [
            Cell(
                row=i,
                col=j,
                value="",
            )
            for i in range(settings.ROWS)
            for j in range(settings.COLUMNS)
        ]

        self.window_opened = False
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = tuple(f"C{i}" for i in range(settings.COLUMNS))

        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)

        for i in range(settings.ROWS):
            self.tree.insert(
                "",
                "end",
                text=f"R{i}",
                values=tuple("" for _ in range(settings.COLUMNS)),
            )

        self.tree.bind("<Double-1>", self.edit_row)

        self.tree["displaycolumns"] = self.tree["columns"]
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.load_data_from_google_drive()

    def convert_to_coord(self, row: str, col: str) -> tuple[int, int]:
        row = (int(row.replace("R", "")),)
        column = (int(col.replace("C", "")),)
        return row, column

    def refresh_values(self, cells: list[Cell]):
        for cell in cells:
            if cell.value:
                values = self.tree.item(f"I{(3-len(str(cell.col))) * '0'}{cell.col+1}")[
                    "values"
                ]
                values[cell.row] = cell.value
                self.tree.item(
                    f"I{(3-len(str(cell.col))) * '0'}{cell.col+1}", values=values
                )

    def edit_row(self, event):
        selected_item = self.tree.selection()

        if selected_item and not self.window_opened:
            col = self.tree.identify_column(event.x)
            row = self.tree.identify_row(event.y)
            ccol, crow = Cell.get_coord(col, row)

            if crow == -1:
                return
            cell: Cell = self.cells[crow * settings.COLUMNS + ccol]
            value = cell.expression if cell.expression else cell.value
            edit_window = tk.Toplevel(self)
            edit_window.title("Edit Row")
            self.window_opened = True

            def close():
                self.window_opened = False
                edit_window.destroy()

            edit_window.protocol("WM_DELETE_WINDOW", close)
            value_entry = tk.Entry(edit_window)

            value_entry.insert(0, value)

            value_entry.pack()

            def update_values():
                updated_values = value_entry.get()

                col = self.tree.identify_column(event.x)
                row = self.tree.identify_row(event.y)
                ccol, crow = Cell.get_coord(col, row)
                cell: Cell = self.cells[crow * settings.COLUMNS + ccol]
                expression = Expression(updated_values, cell)

                if expression.parse():
                    updated_values = expression.evaluate(self.cells)

                cell.value = updated_values
                values = self.tree.item(selected_item)["values"]
                values[crow] = updated_values

                self.tree.item(selected_item, values=values)

                for dcell in cell._depends_on_me:
                    dcell.value = Expression(dcell.expression, dcell).evaluate(
                        self.cells
                    )

                self.refresh_values(cell._depends_on_me)

                close()

            update_button = tk.Button(edit_window, text="Update", command=update_values)
            update_button.pack()

    def load_data_from_google_drive(self):
        pass

    def add_data(self):
        name = self.name_entry.get()
        size = self.size_entry.get()
        self.tree.insert("", "end", values=(name, size))
        self.name_entry.delete(0, tk.END)
        self.size_entry.delete(0, tk.END)

    def edit_data(self):
        selected_item = self.tree.selection()
        if selected_item:
            name = self.name_entry.get()
            size = self.size_entry.get()
            self.tree.item(selected_item, values=(name, size))
            self.name_entry.delete(0, tk.END)
            self.size_entry.delete(0, tk.END)


if __name__ == "__main__":
    app = SpreadsheetApp()
    app.mainloop()
