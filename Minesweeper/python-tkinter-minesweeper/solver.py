import reader
import interact

'''
Scaffolding for solver AI later.
Holds functions that will be used for patterns
'''

"""
Function at this moment should fail
the paramter 'board' needs to be from an return from ai.py
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


def find_mines(board):
    """Return coordinates to flag, assuming existing flags are correct."""
    rows, columns = board.shape
    tiles_to_flag = set()

    for row in range(rows):
        for col in range(columns):
            number = board[row, col]

            # Only revealed numbers provide a mine count for this rule.
            if not 1 <= number <= 8:
                continue

            flagged_count = 0
            unknown_neighbors = []

            for neighbor_row, neighbor_col in get_neighbors(board, row, col):
                neighbor = board[neighbor_row, neighbor_col]

                if neighbor == reader.FLAG:
                    flagged_count += 1
                elif neighbor == reader.UNKNOWN:
                    unknown_neighbors.append((neighbor_row, neighbor_col))

            remaining_mines = number - flagged_count

            if unknown_neighbors and remaining_mines == len(unknown_neighbors):
                tiles_to_flag.update(unknown_neighbors)

    return tiles_to_flag


def find_safe_tiles(board):
    """Return coordinates safe to reveal beside revealed empty tiles."""
    rows, columns = board.shape
    safe_tiles = set()

    for row in range(rows):
        for col in range(columns):
            # EMPTY is a revealed zero; UNKNOWN (0) is still covered.
            if board[row, col] != reader.EMPTY:
                continue

            for neighbor_row, neighbor_col in get_neighbors(board, row, col):
                if board[neighbor_row, neighbor_col] == reader.UNKNOWN:
                    safe_tiles.add((neighbor_row, neighbor_col))

    return safe_tiles


def find_safe_tiles_from_total(board, total_mines):
    """If all mines have been correctly flagged, every remaining covered tile is safe"""
    rows, columns = board.shape
    unknown_tiles = []
    total_flagged = 0
    safe_tiles = set()

    for row in range(rows):
        for col in range(columns):
            # if the tile is covered and has not been flagged yet
            if board[row, col] == reader.UNKNOWN:
                unknown_tiles.append((row,col))
            # if the tile has been flagged
            elif board[row, col] == reader.FLAG:
                total_flagged += 1
    
    # if the number of flagged tiles is equal to number of mines, then there are no more mines
    if total_flagged == total_mines:
        safe_tiles.update(unknown_tiles)

    return safe_tiles