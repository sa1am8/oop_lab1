from models import Cell
from settings import get_settings, Settings


settings: Settings = get_settings()


class FileManager:
    def save_file(cells: list[Cell]):
        values = FileManager._compose_file(cells)

        body = {
            "values": values,
        }
        return body

    def load_file(sheet, cells: list[Cell]):
        values = sheet.get("values", [])
        formulas = sheet.get("formulas", {})

        FileManager._decompose_file(values, formulas, cells)

    def _decompose_file(values, formulas, cells: list[Cell]):
        for row_idx, row in enumerate(values):
            for col_idx, cell_value in enumerate(row):
                cells[settings.COLUMNS * (row_idx) + (col_idx)] = Cell(
                    row=row_idx,
                    col=col_idx,
                    value=cell_value,
                    expression=formulas.get(f"{row_idx}:{row_idx}", {}).get(
                        f"C{col_idx}"
                    ),
                )

    def _compose_file(cells: list[Cell]):
        return [
            [
                {"userEnteredValue": {"formulaValue": cell.expression}}
                if cell.expression
                else cell.value
                for cell in cells[i : i + settings.COLUMNS]
            ]
            for i in range(0, len(cells), settings.COLUMNS)
        ]
