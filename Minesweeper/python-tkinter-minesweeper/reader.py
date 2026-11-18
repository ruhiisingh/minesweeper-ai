import numpy as np
import minesweeper as ms

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
E.g. changes to first row, gets reflected on every row.
'''

"""
Create empty board, which probably is dumb
since this file might need to be ran after each step,
swap the print statement to return later.
AI needs to be given the board for later CSP related
development, statistical method.
"""
def boardInit(rows, columns):
    return np.zeros((rows, columns), dtype=np.int8)


"""
Improvements to this later could possibly be keeping running
memory of the board, so making an infinite loop
but if running agents in parallel unsure of how this ends up.
Also keeping a database for training bots, would be reducing
drive lifespan due to frequent read/

game would be passed from a different file ai.py
since one file 'owns' the game itself
so calling a minesweeper instance makes it's own independent game
which is separate from the one the ai can access.
"""
def readBoard(game):
    # Create empty game board, non-static
    rows = len(game.tiles)
    columns = len(game.tiles[0])
    board = boardInit(rows, columns)

    # read the game visually
    # reads from left to right then goes down one row & repeats
    for row in range(rows):
       for column in range(columns):
        tile = game.tiles[row][column]

        if tile["state"] == ms.STATE_FLAGGED:
            board[row, column] = FLAG

        elif tile["state"] == ms.STATE_CLICKED:
            count = tile["mines"]
            board[row, column] = EMPTY if count == 0 else count
        # Covered tiles remain UNKNOWN, the initial value.
        # Else would be values greater than 0 so "plain" 1~8
        # Flags are already taken into account earlier, leaving just non-mine or mine tiles
    return board
