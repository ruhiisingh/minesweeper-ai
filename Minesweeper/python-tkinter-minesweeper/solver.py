import reader as reads
'''
Scaffolding for solver AI later.
Holds functions that will be used for patterns later
'''

"""
Directly taken from the repository which supplied the game
will have to call this quite frequently so make it cheap.
Paramter board comes from reader.py which is imported
"""
def get_neighbors(board, row, col):
    rows, columns = board.shape

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
        """
        if 0 <= neighbor_row < rows and 0 <= neighbor_col < columns:
            neighbors.append((neighbor_row, neighbor_col))

    return neighbors
