import tkinter as tk
import minesweeper as ms

"""
Game state is already being stored in game being ran in minesweeper.py
"""

def main():

    # Starts the game, by running the game
    window = tk.Tk()
    game = ms.Minesweeper(window)
    window.mainloop()


if __name__ == "__main__":
    main()
