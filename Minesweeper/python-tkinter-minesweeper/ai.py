import tkinter as tk
import minesweeper as ms
import reader
import interact
import solver
import snapshot
from pathlib import Path
import numpy as np


"""
file used to for staging various components together
better for later abstraction and more higher-level visualization
"""
def training(game, board):
    features = []
    outcomes = []

    rows, cols = board.shape

    for row in range(rows):
        for col in range(cols):
            #training on covered tiles
            if board[row, col] != reader.UNKNOWN:
                continue
            attributes = solver.get_tree_attributes(board, row, col)

            #Skip tiles with no info
            if all(value == reader.UNKNOWN or value == solver.EDGE for value in attributes):
                continue

            features.append(attributes)

            #Train only on hidden tiles
            if game.tiles[row][col]["isMine"]:
                outcomes.append(1) #Mine
            else:
                outcomes.append(0) #Not Mine

    return features, outcomes







def main():
    #Create file to store training data
    INFO_PATH = Path(__file__).resolve().parent / "training_data.npz"

    #Load old data if there is any
    if INFO_PATH.exists():
        with np.load(str(INFO_PATH)) as old_data:
                train_X = old_data["X"].tolist()
                train_Y = old_data["Y"].tolist()
                print("Load old data", len(train_X))
    else:
        train_X = []
        train_Y = []

    # Starts the game, by running minesweeper.py
    window = tk.Tk()
    window.title("Minesweeper")

    game = ms.Minesweeper(window)

    def turn():
        board = reader.readBoard(game)

        new_X, new_Y = training(game, board)

        train_X.extend(new_X)
        train_Y.extend(new_Y)

        if train_X:
            np.savez(str(INFO_PATH), X = np.array(train_X, dtype = np.int8), Y = np.array(train_Y, dtype = np.int8))

        # Checks if the board has been untouched
        # If so, then do an opening move
        if (board == reader.UNKNOWN).all():
            interact.reveal(game, row=0, column=0)

        # Orchestrates next move
        # Reads all flags & places them if unsafe
        else:
            tiles_to_flag = solver.find_mines(board)
            tiles_to_flag.update(solver.find_mines_from_total(board, game.mines))
            safe_tiles = solver.find_safe_tiles(board)
            safe_tiles.update(
                solver.find_safe_tiles_from_total(board, game.mines)
            )

            # Try more expensive comparisons only when the simple rules find nothing.
            if not tiles_to_flag and not safe_tiles:
                advanced_safe, advanced_mines = solver.find_advanced_moves(board)
                safe_tiles.update(advanced_safe)
                tiles_to_flag.update(advanced_mines)

            if tiles_to_flag:
                row, column = min(tiles_to_flag)
                interact.flag(game, row, column)

            elif safe_tiles:
                row, column = min(safe_tiles)
                interact.reveal(game, row, column)

            else:
                path = snapshot.save_snapshot(board, game.tiles)
                if path is None:
                    print(
                        "NO other safe move. Snapshot skipped: "
                        "fewer than two revealed tiles."
                    )
                else:
                    print(f"NO other safe move. Snapshot saved to: {path}")
                return

        window.after(1, turn)

    # every second inspect the board.
    # Remove later, or instead probably figure out a stack method that calls patterns, or just make the ai do stuff
    window.after(1, turn)
    window.mainloop()


# Needed this since it would run the main of minesweeper.py instead
if __name__ == "__main__":
    main()
