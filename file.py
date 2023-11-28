from models import Cell
from settings import get_settings, Settings
import re

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
                cells[row_idx][col_idx] = Cell(
                    row=row_idx,
                    col=col_idx,
                    value=cell_value,
                    expression=formulas.get(f"{row_idx}:{row_idx}", {}).get(
                        f"C{col_idx}"
                    ),
                )

    def _compose_expression(expression: str) -> str:
        # change [C%d:R%d] to char(row)int(col) by regex
        # [C0:R3] -> A1
        expression = re.sub(
            r"\[C(\d+):R(\d+)\]",
            lambda match: f"{chr(int(match.group(2)) + 65)}{int(match.group(1)) + 1}",
            expression,
        )
        return "=" + expression

    def _compose_file(cells: list[Cell]):
        return [
            [
                FileManager._compose_expression(cell.expression)  # noqa E501
                if cell.expression
                else cell.value
                for cell in cell_row
            ]
            for cell_row in cells
        ]
