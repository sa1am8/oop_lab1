import re

from models import Cell
from settings import get_settings, Settings

settings: Settings = get_settings()


class Expression:
    def __init__(
        self,
        expression,
        cell,
    ):
        self.expression = expression
        self.current_index = 0
        self.cell = cell

    def parse(self):
        self.current_index = 0
        if not self.expression.startswith("="):
            return

        self.expression = self.expression[1:]
        self.expression = self.expression.replace(" ", "")
        try:
            return self._parse_expression()
        except ValueError:
            return

    def _parse_expression(self):
        node = self._parse_term()
        while self.current_index < len(self.expression) and self.expression[
            self.current_index
        ] in ("+", "-", "*", "/"):
            operator = self.expression[self.current_index]
            self.current_index += 1
            right_node = self._parse_term()
            node = {
                "type": "binary_operation",
                "operator": operator,
                "left": node,
                "right": right_node,
            }
        return node

    def _parse_term(self):
        if self.expression[self.current_index] == "(":
            self.current_index += 1
            node = self._parse_expression()
            if self.expression[self.current_index] == ")":
                self.current_index += 1
                return node
            else:
                raise ValueError("Mismatched parentheses")

        elif (
            self.expression[self.current_index].isdigit()
            or self.expression[self.current_index] == "."
        ):
            start_index = self.current_index
            while self.current_index < len(self.expression) and (
                self.expression[self.current_index].isdigit()
                or self.expression[self.current_index] == "."
            ):
                self.current_index += 1
            return {
                "type": "number",
                "value": float(
                    self.expression[start_index : self.current_index]  # noqa E203
                ),
            }
        elif re.match(
            r"\[C\d+:R\d+\]", self.expression[self.current_index :]  # noqa E203
        ):
            match = re.match(
                r"\[C\d+:R\d+\]", self.expression[self.current_index :]  # noqa E203
            )
            self.current_index += match.end()
            return {"type": "cell_reference", "value": match.group()}
        else:
            raise ValueError("Wrong expression")

    def evaluate(self, cells) -> str:
        self.current_index = 0

        try:
            node = self._parse_expression()

            if node is None:
                return self.expression

            res = self._evaluate_node(node, cells)
            self.cell.expression = self.expression
            return str(res)
        except ValueError as e:
            self.cell.expression = ""
            return e.args[0]

    def _evaluate_cell_reference(self, cell_reference: str, cells: list[Cell]):
        cell_reference = cell_reference[1:-1]
        col = int(cell_reference.split(":")[0].replace("C", ""))
        row = int(cell_reference.split(":")[1].replace("R", ""))

        cell: Cell = cells[col * settings.ROWS + row]
        self.cell._i_depend_on.add(cell)
        cell._depends_on_me.add(self.cell)

        try:
            return float(cell.value)
        except ValueError:
            raise ValueError(
                "Number expected in cell reference - " + cell_reference
            )  # noqa E501

    def _evaluate_node(self, node, cells):
        if node["type"] == "number":
            return node["value"]
        elif node["type"] == "cell_reference":
            return self._evaluate_cell_reference(node["value"], cells)
        elif node["type"] == "binary_operation":
            left = self._evaluate_node(node["left"], cells)
            right = self._evaluate_node(node["right"], cells)
            if node["operator"] == "+":
                return left + right
            elif node["operator"] == "-":
                return left - right
            elif node["operator"] == "*":
                return left * right
            elif node["operator"] == "/":
                return left / right
        elif node["type"] == "error":
            return node["value"]
