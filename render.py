import tkinter as tk
from tkinter import ttk

from settings import get_settings, Settings
from models import Cell
from expression import Expression
from google_drive import driver
from file import FileManager


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

        button_save = tk.Button(self, text="Save", command=self.save_file)
        button_save.pack()

        self.tree["displaycolumns"] = self.tree["columns"]
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.button_add = tk.Button(self, text="Add", command=self.add_row)
        self.button_add.pack()

    def save_file(self):
        message = tk.Label(self, text="File was saved")
        message.pack()
        message.after(5000, message.destroy)

        body = FileManager.save_file(self.cells)
        driver.save_sheet(settings.FILE_ID, body)

    def convert_to_coord(self, row: str, col: str) -> tuple[int, int]:
        row = (int(row.replace("R", "")),)
        column = (int(col.replace("C", "")),)
        return row, column

    def refresh_values(self, cells: list[Cell] | set[Cell]):
        for cell in cells:
            if cell.value:
                values = self.tree.item(
                    f"I{(3-len(str(cell.col))) * '0'}{cell.col+1}"
                )[  # noqa E501
                    "values"
                ]
                values[cell.row] = cell.value
                self.tree.item(
                    f"I{(3-len(str(cell.col))) * '0'}{cell.col+1}",
                    values=values,  # noqa E501
                )

    def check_circle(self, cell1: Cell, cell2: Cell):
        if cell1 in cell2._i_depend_on:
            raise ValueError("Circular dependency")

    def update_dependent_cells(self, cell: Cell):
        cells_to_update = set()

        for dcell in cell._depends_on_me:
            self.check_circle(dcell, cell)

            dcell.value = Expression(dcell.expression, dcell).evaluate(self.cells)
            cells_to_update.add(dcell)
            for cell in self.update_dependent_cells(dcell):
                cells_to_update.add(cell)

        return cells_to_update

    def edit_row(self, event):
        selected_item = self.tree.selection()

        if selected_item and not self.window_opened:
            col = self.tree.identify_column(event.x)
            row = self.tree.identify_row(event.y)
            crow, ccol = Cell.get_coord(col, row)

            if ccol == -1:
                return
            cell: Cell = self.cells[ccol * settings.COLUMNS + crow]
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
                crow, ccol = Cell.get_coord(col, row)
                cell: Cell = self.cells[crow * settings.COLUMNS + ccol]
                expression = Expression(updated_values, cell)

                if expression.parse():
                    updated_values = expression.evaluate(self.cells)

                cell.value = updated_values
                values = self.tree.item(selected_item)["values"]
                values[ccol] = updated_values

                self.tree.item(selected_item, values=values)
                try:
                    cells_to_update = self.update_dependent_cells(cell)
                    self.refresh_values(cells_to_update)

                except ValueError as e:
                    cell.value = str(e)
                    for dcell in cell._i_depend_on:
                        dcell.value = str(e)
                    for dcell in cell._depends_on_me:
                        dcell.value = str(e)

                    self.refresh_values(cell._i_depend_on)
                    self.refresh_values(cell._depends_on_me)
                    self.refresh_values([cell])

                close()

            update_button = tk.Button(
                edit_window, text="Update", command=update_values
            )  # noqa E501
            update_button.pack()

    def add_row(self):
        row = self.tree.get_children()[-1]
        row_index = int(self.tree.item(row)["text"].replace("R", "")) + 1
        settings.ROWS += 1

        self.tree.insert(
            "",
            "end",
            text=f"R{row_index}",
            values=["" for _ in range(settings.COLUMNS)],
        )  # noqa E501
        for i in range(settings.COLUMNS):
            self.cells.append(
                Cell(row=row_index, col=i, value="", expression="")
            )  # noqa E501

    def edit_data(self):
        selected_item = self.tree.selection()
        if selected_item:
            name = self.name_entry.get()
            size = self.size_entry.get()
            self.tree.item(selected_item, values=(name, size))
            self.name_entry.delete(0, tk.END)
            self.size_entry.delete(0, tk.END)
