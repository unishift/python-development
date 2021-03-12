import random
from functools import partial

import tkinter as tk


class Grid(tk.Frame):
    def __init__(self, master=None, nb_rows=4, nb_cols=4):
        super().__init__(master=master)

        self.nb_rows = nb_rows
        self.nb_cols = nb_cols

        self.buttons = []

        self.grid()
        self.reset()

    def reset(self):
        for button in self.buttons:
            button.destroy()

        self.freeze = False

        self.generate_grid()
        self.create_widgets()
        self.position_widgets()

    def generate_grid(self):
        self.numbers = list(range(self.nb_rows * self.nb_cols - 1))
        self.numbers.append(None)
        random.shuffle(self.numbers)

    def get_number_pos(self, number):
        pos = self.numbers.index(number)
        row, col = pos // self.nb_cols, pos % self.nb_cols

        return pos, row, col

    def position_widgets(self):
        for number in self.numbers:
            if number is None:
                continue

            pos, row, col = self.get_number_pos(number)
            self.buttons[number].grid(row=row, column=col)

    def win_condition(self):
        return self.numbers == list(range(len(self.numbers) - 1)) + [None]

    def on_press(self, number):
        if self.freeze:
            return

        button_pos, button_row, button_col = self.get_number_pos(number)
        empty_pos, empty_row, empty_col = self.get_number_pos(None)

        if abs(button_row - empty_row) + abs(button_col - empty_col) == 1:
            self.numbers[button_pos], self.numbers[empty_pos] = self.numbers[empty_pos], self.numbers[button_pos]

        self.position_widgets()

        if self.win_condition():
            self.master.endgame()

    def create_widgets(self):
        self.buttons = [
            tk.Button(self, text=str(number + 1), command=partial(self.on_press, number))
            for number in range(len(self.numbers) - 1)
        ]


class GameOf15(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.create_widgets()

    def endgame(self):
        self.button_grid.freeze = True
        print('Congratulations!')

    def reset(self):
        self.button_grid.reset()

    def create_widgets(self):
        self.utility_row = tk.Frame(self)
        self.new_button = tk.Button(self.utility_row, text='New', command=self.reset)
        self.new_button.grid(row=0, column=0)
        self.exit_button = tk.Button(self.utility_row, text='Exit', command=self.quit)
        self.exit_button.grid(row=0, column=1)
        self.utility_row.grid()

        self.button_grid = Grid(self)


if __name__ == '__main__':
    app = GameOf15()
    app.master.title('Game of 15')
    app.mainloop()
