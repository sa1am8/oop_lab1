from models import Cell


class FileManager:
    def save_file():
        pass

    def load_file(sheet, cells: list[Cell]):
        values = sheet.get("values", [])
        formulas = sheet.get("formulas", {})

        FileManager._decompose_file(values, formulas, cells)

    def _decompose_file(values, formulas, cells: list[Cell]):
        for row_idx, row in enumerate(values, start=1):
            for col_idx, cell_value in enumerate(row, start=1):
                cells.append(
                    Cell(
                        row=row_idx,
                        col=col_idx,
                        value=cell_value,
                        expression=formulas.get(f"{row_idx}:{row_idx}", {}).get(
                            f"C{col_idx}"
                        ),
                    )
                )

    def _compose_file():
        pass
