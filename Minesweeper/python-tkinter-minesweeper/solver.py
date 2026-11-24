import reader
EDGE = -1
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
            num = board[row, col]

            # EMPTY is a revealed zero; UNKNOWN (0) is still covered.
            if board[row, col] == reader.EMPTY:
                num = 0
            elif not 1 <= num <= 8:
                continue

            # Initialization, to get tiles revealed
            flagged_neighbors = 0
            unknown_neighbors = []

            """
            For a target tile, retrieve all neighbors
            define how many neighboring tiles are flagged.
            Check if num of flagged tiles matches target,
            if so update & in main function reveal neighbors
            deemed safe.
            """
            for neighbor_row, neighbor_col in get_neighbors(board, row, col):
                neighbor = board[neighbor_row, neighbor_col]

                if neighbor == reader.FLAG:
                    flagged_neighbors += 1
                elif neighbor == reader.UNKNOWN:
                    unknown_neighbors.append((neighbor_row, neighbor_col))
            if flagged_neighbors == num:
                safe_tiles.update(unknown_neighbors)

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

"""
Pairwise based method of solving the board, which calculates a partial frontier state.
It'll be more of the statistical/arithmetic method, where there is a forced move which might
help progress fowards, but when there is no defined move from this check. Along with the earlier checks
in ai.py, means we have to rely on decision trees from here, or find some other method of progression.
"""
def find_pattern_moves(board):
    """
    Return (safe_tiles, tiles_to_flag) using pairwise clue constraints.

    Existing flags are assumed to be correct.
    Preliminary pretty much half asses attempt for CSP related solving.
    More of an pattern checker than anything.
    """
    rows, columns = board.shape
    constraints = {}

    for row in range(rows):
        # Vist each tile
        for col in range(columns):
            number = board[row, col]

            if number == reader.EMPTY:
                number = 0
            elif not 1 <= number <= 8:
                continue

            unknown = set()
            flagged = 0
            # Check target/clue tile's neighbors
            # Count flagged versus unknown tiles in neighbors
            for neighbor_row, neighbor_col in get_neighbors(board, row, col):
                value = board[neighbor_row, neighbor_col]

                if value == reader.FLAG:
                    flagged += 1
                elif value == reader.UNKNOWN:
                    unknown.add((neighbor_row, neighbor_col))
            """
            Remaning produces the constraint, e.g. tile reveals clue 3.
            With a adjacent flag the constraint A + B + C = 2 is made.
            """
            remaining = int(number) - flagged

            if not 0 <= remaining <= len(unknown):
                raise ValueError(
                    f"Clue at {(row, col)} conflicts with neighboring flags."
                )

            if not unknown:
                continue

            cells = frozenset(unknown)

            if cells in constraints and constraints[cells] != remaining:
                raise ValueError("The same cells have conflicting mine counts.")
            # Stores the relationship, basically keeps all the mine-count equations
            # Across many different simulations
            constraints[cells] = remaining

    safe_tiles = set()
    tiles_to_flag = set()

    # Checks the constraints independently, where 0 is equivalent to no mines remaining
    # 1 is where each cell must contain a mine
    for cells, remaining in constraints.items():
        if remaining == 0:
            safe_tiles.update(cells)
        elif remaining == len(cells):
            tiles_to_flag.update(cells)

    # Loops through comparisons of constraints, no-double counting
    # e.g. Constaint 1 vs Constraint 0
    # Then Constraint 0 vs Constraint 1 is ignored later
    items = list(constraints.items())
    # enumerate(items) is the position + constraint
    for index, (left, left_count) in enumerate(items):
        # items[index + 1] is the following constraint
        for right, right_count in items[index + 1:]:
            shared = left & right

            if not shared:
                continue

            left_only = left - right
            right_only = right - left

            # Both clues constrain how many mines can occupy their overlap.
            # E.g. in the 1 2 1 pattern, if theres a mine in the center
            # where 2 is located, it satisfies both clue 1, but clue 2 is not satisfied
            # so there is no shared mines between clue's 1.
            shared_min = max(
                0,
                left_count - len(left_only),
                right_count - len(right_only),
            )
            shared_max = min(
                len(shared),
                left_count,
                right_count,
            )

            if shared_min > shared_max:
                raise ValueError("Overlapping clues have conflicting counts.")

            groups = (
                (shared, shared_min, shared_max),
                (
                    left_only,
                    left_count - shared_max,
                    left_count - shared_min,
                ),
                (
                    right_only,
                    right_count - shared_max,
                    right_count - shared_min,
                ),
            )

            # Finds forced moves in the groups defined above
            # Exlcusive & shared groups are tested here
            for cells, minimum, maximum in groups:
                if not cells:
                    continue

                if maximum == 0: # group must not have a mine
                    safe_tiles.update(cells)
                elif minimum == len(cells): # all cells must contain a mine
                    tiles_to_flag.update(cells)

    if safe_tiles & tiles_to_flag:
        raise ValueError("Conflicting deductions: a tile is both safe and mined.")

    return safe_tiles, tiles_to_flag


def get_tree_attributes(board, row, col):
    rows, columns = board.shape

    # Formatted to make it easier for later stuff
    offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]

    attributes = []

    for row_offset, col_offset in offsets:
        neighbor_row = row + row_offset
        neighbor_col = col + col_offset
        """
        Edge case, target tile e.g. bottom left corner, it's neighbors to it's left and bottom just do not exist.
        This basically covers those issues and just wont append them to the list that gets returned.
        Game makes use of this and i just moved it over here as well
        """
        if 0 <= neighbor_row < rows and 0 <= neighbor_col < columns:
            attributes.append(int(board[neighbor_row, neighbor_col]))
        #Makes any edge read in -1
        else:
            attributes.append(EDGE)
    return attributes
