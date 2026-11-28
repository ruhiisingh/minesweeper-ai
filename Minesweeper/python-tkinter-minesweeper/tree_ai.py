import tkinter as tk
import minesweeper as ms 
import reader 
import interact
import tree_solver
import snapshot


def save_failure_snapshot(game, board, reason):
    try:
        path = snapshot.save_snapshot(board, game.tiles)
    except OSError as error:
        print(f"{reason}. Snapshot failed: {error}")
        return

    if path is None:
        print(f"{reason}. Snapshot skipped: fewer than two revealed tiles.")
    else:
        print(f"{reason}. Snapshot saved to: {path}")


class TreeMinesweeper(ms.Minesweeper):
    def gameOver(self, won):
        if not won:
            # Capture the board before the parent can show a dialog and restart.
            save_failure_snapshot(self, reader.readBoard(self), "Game lost")
        super().gameOver(won)


def main():

    move_count = {"Solver_flags" : 0, "Solver_safest_moves": 0, "tree_moves": 0 }
    window = tk.Tk()
    window.title("Minesweeper Tree")

    game = TreeMinesweeper(window)

    #Load model
    model = tree_solver.load_model()

    def turn():
        board = reader.readBoard(game)

        move = tree_solver.choose_move(board, model, game.mines)
        if move is None:
            save_failure_snapshot(game, board, "No Move")
            return

        source, row, column = move
        if source == "flag":
            move_count["Solver_flags"] += 1
            interact.flag(game, row, column)
        else:
            if source == "safe":
                move_count["Solver_safest_moves"] += 1
            elif source == "tree":
                move_count["tree_moves"] += 1
            interact.reveal(game, row, column)
        
        window.after(100, turn)

    window.after(100, turn)
    window.mainloop()
    
    print("Rule flags:", move_count["Solver_flags"])
    print("Rule safe moves:", move_count["Solver_safest_moves"])
    print("Tree moves:", move_count["tree_moves"])

if __name__ == "__main__":
    main()
                
