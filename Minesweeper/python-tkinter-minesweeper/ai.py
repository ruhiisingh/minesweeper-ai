import tkinter as tk
import minesweeper as ms
import reader
import interact
import solver

"""
file used to for staging various components together
better for later abstraction and more higher-level visualization
"""

def main():
    # Starts the game, by running minesweeper.py
    window = tk.Tk()
    window.title("Minesweeper")

    game = ms.Minesweeper(window)

    def turn():
        board = reader.readBoard(game)

        # Checks if the board has been untouched
        # If so, then do an opening move
        if (board == reader.UNKNOWN).all():
            interact.reveal(game, row=0, column=0)

        # Orchestrates next move
        # Reads all flags & places them if unsafe
        else:
            tiles_to_flag = solver.find_mines(board)
            safe_tiles = solver.find_safe_tiles(board)

            """Flags work, but current issue seems to be lack of info
            from the elif statement below to reveal tiles deemed safe"""
            if tiles_to_flag:
                row, column = min(tiles_to_flag)
                interact.flag(game, row, column)

            # Not sure why this isn't defining safe tiles just yet
            elif safe_tiles:
                row, column = min(safe_tiles)
                interact.reveal(game, row, column)

            else:
                print("NO other safe move")
                return

        window.after(1000, turn)

    # every second inspect the board.
    # Remove later, or instead probably figure out a stack method that calls patterns, or just make the ai do stuff
    window.after(1000, turn)
    window.mainloop()


# Needed this since it would run the main of minesweeper.py instead
if __name__ == "__main__":
    main()
