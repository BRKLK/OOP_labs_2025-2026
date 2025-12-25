from enum import Enum
from tkinter import NO
from typing import Self
import os
import json
import types

script_dir = os.path.dirname(os.path.abspath(__file__))
path5 = os.path.join(script_dir, "font5.json")
path7 = os.path.join(script_dir, "font7.json")

with open(path5, "r") as f:
    font5: dict = json.load(f)
with open(path7, "r") as f:
    font7: dict = json.load(f)


class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class Printer():
    def __init__(self, font: dict, color: Color, position: tuple[int, int], symbol: str):
        self.font = font
        self.color = color
        self.position = position
        self.symbol = symbol
    
    @classmethod
    def print_text(cls, text: str, font: dict, color: Color, position: tuple[int, int], symbol: str):
        P = cls(color, position, symbol)
        P.print(text)

    def print(self, text: str):
        x, y = self.position

        print("\n" * x, end="")

        num_of_lines = len(list(self.font.values())[0])

        rows = ['' + (' ' * y)] * (num_of_lines + 2)
        for smbl in text.upper():
            for i, line in enumerate(self.font[smbl]):
                rows[i] += line + (" " * 2)
        
        for row in rows:
            print(self.color.value + row.replace("*", self.symbol))
    
    def __enter__(self):
        return self
    
    def __exit__(
            self,
            exc_type: type | None,
            exc_value: BaseException | None,
            traceback: types.TracebackType | None
    ) -> None:
        print(Color.RESET.value, end="")
        


# Printer.print_text("Hello, world!", Color.RED, (5, 10), "5")

with Printer(font7, Color.GREEN, (2, 3), "$") as printer:
    printer.print("Hello,")
    printer.print("World!")

with Printer(font5, Color.BLUE, (2, 3), "0") as printer:
    printer.print("Hello,")
    printer.print("World!")