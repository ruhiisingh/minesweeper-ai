import reader
'''
Scaffolding for solver AI later.
Holds functions that will be used for patterns
'''

"""
Function at this moment should fail
the paramter 'board' needs to be from an return from reader.py
minesweeper.py has a similar function called getNeighbors
however that requires object 'self' from the minesweeper class
"""
def get_neighbors(board, row, col):
    rows, columns = board.shape

    # Formatted to make it easier for later stuff
    offsets = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]

    neighbors = []

    for row_offset, col_offset in offsets:
        neighbor_row = row + row_offset
        neighbor_col = col + col_offset
        """
        Edge case, target tile e.g. bottom left corner, it's neighbors to it's left and bottom just do not exist.
        This basically covers those issues and just wont append them to the list that gets returned.
        Game makes use of this and i just moved it over here as well
        """
        if 0 <= neighbor_row < rows and 0 <= neighbor_col < columns:
            neighbors.append((neighbor_row, neighbor_col))

    return neighbors
