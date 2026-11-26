import tkinter as tk
import minesweeper as ms 
import reader 
import interact
import tree_solver
import solver

def main():

    move_count = {"Solver_flags" : 0, "Solver_safest_moves": 0, "tree_moves": 0 }
    window = tk.Tk()
    window.title("Minesweeper Tree")

    game = ms.Minesweeper(window)

    #Load model
    model = tree_solver.load_model()

    def turn():
        board = reader.readBoard(game)

        #First move
        if (board == reader.UNKNOWN).all():
            interact.reveal(game, row = 0, column = 0)

        else:

            solver_mines = solver.find_mines(board)

            solver_safe_tiles = solver.find_safe_tiles(board)

            '''
            tiles_to_flag = tree_solver.find_mines(board, model, threshold = 0.99)

            safe_tiles = tree_solver.find_safe_tiles(board, model)
            '''

            if(solver_mines):
                row, column = min(solver_mines)
                move_count["Solver_flags"] += 1
                interact.flag(game, row, column)
            

            elif solver_safe_tiles:
                row, column = min(solver_safe_tiles)
                move_count["Solver_safest_moves"] += 1
                interact.reveal(game, row, column)

            else:
                safes_tile = tree_solver.find_safest_tile(board, model)

                if safes_tile is None:
                    print("No Move")
                    return
                
                move_count["tree_moves"] += 1
                row, column = safes_tile
                interact.reveal(game, row, column)
        
        window.after(100, turn)

    window.after(100, turn)
    window.mainloop()
    
    print("Rule flags:", move_count["Solver_flags"])
    print("Rule safe moves:", move_count["Solver_safest_moves"])
    print("Tree moves:", move_count["tree_moves"])

if __name__ == "__main__":
    main()
                
