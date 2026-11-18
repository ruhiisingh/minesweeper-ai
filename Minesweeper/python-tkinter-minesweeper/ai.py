import tkinter as tk
import minesweeper as ms

"""
file used to for staging various components together
better for later abstraction and more higher-level visualization
"""

def main():

    # Starts the game, by running minesweeper.py
    window = tk.Tk()
    game = ms.Minesweeper(window)
    window.mainloop()


if __name__ == "__main__":
    main()
