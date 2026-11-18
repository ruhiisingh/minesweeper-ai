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
        # Output is terminal junk remove later
        print(board)

        # Pass the board later to solver.py
        # Probably gonna need a mega loop
        window.after(1000, inspect_board)

    # every second inspect the board.
    # Remove later, or instead probably figure out a stack method that calls patterns, or just make the ai do stuff
    window.after(1000, inspect_board)
    window.mainloop()


# Needed this since it would run the main of minesweeper.py instead
if __name__ == "__main__":
    main()
