import tkinter as tk
import minesweeper as ms
import reader

"""
file used to for staging various components together
better for later abstraction and more higher-level visualization
"""

def main():

    # Starts the game, by running minesweeper.py
    window = tk.Tk()
    window.title("Minesweeper")

    game = ms.Minesweeper(window)

    def inspect_board():
        board = reader.readBoard(game)

        # Currently using as a debug, remove once using solver.py
        print(board)

        # Pass the board later to solver.py
        window.after(1000, inspect_board)


    window.after(1000, inspect_board)
    window.mainloop()


if __name__ == "__main__":
    main()
