import numpy as np

"""
The game's entire game state is stored in minesweeper.py
though it loses fog of war, where everything revealed from start
file serves to abstract the game data from the AI.
"""

# Initializing mappings for tiling.
UNKNOWN = 0 # tile not pressed yet
# Mine values 1~8 omitted since they can be directly used
EMPTY = 9 # tile pressed
FLAG = 10 # expected mine positon
EXPLODED_MINE = 11 # game lose condition

'''
initialize 2D array using rows then columns
numpy required since other implementations caused
the array of lists to reference the same memory space.
E.g. changes to first row, gets reflected on every since row.
'''
def boardInit(rows=10, columns=10):
    return np.zeros((rows, columns), dtype=np.int8)

"""
Create empty board, which probably is dumb
since this file might need to be ran after each step
swap the print statement to return later.
AI needs to be given the board for later CSP related
development.
"""
def main():
    board = boardInit()
    print(board)


if __name__ == "__main__":
    main()
