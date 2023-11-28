class Cell:
    def __init__(
        self, row: int, col: int, value: str = None, expression: str = None
    ):  # noqa E501
        self.row = row
        self.col = col
        self.value = value
        self.expression = expression
        self._depends_on_me = set()
        self._i_depend_on = set()

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = str(value)

    def __repr__(self) -> str:
        return f"Cell({self.row}, {self.col}, {self.value})"

    def get_data(self, col: str, row: str) -> str:
        if col == "0":
            return self.tree.item(row)["text"]
        elif int(col) > len(self.tree.item(row)["values"]):
            return ""
        return self.tree.item(row)["values"][int(col) - 1]

    def get_coord(col: str, row: str) -> tuple[int, int]:
        if row[-1].isdigit():
            row = int(row[-1]) - 1
        else:
            row = ord(row[-1]) - 65 + 10  # 65 is ASCII code for 'A'

        col = int(col.replace("#", "")) - 1
        return row, col
