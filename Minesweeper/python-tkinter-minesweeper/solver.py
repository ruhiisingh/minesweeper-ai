import reader

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

def find_mines_from_total(board, total_mines):
    """Flags remaining tiles if the number of mines left is the number of unflagged covered tiles"""
    rows, columns = board.shape
    unknown_tiles = []
    total_flagged = 0
    mine_tiles = set()

    for row in range(rows):
        for col in range(columns):
            # if the tile is covered and has not been flagged yet
            if board[row, col] == reader.UNKNOWN:
                unknown_tiles.append((row, col))
            # if the tile has been flagged
            elif board[row, col] == reader.FLAG:
                total_flagged += 1

    # calculates the number of mines to locate
    mines_remaining = total_mines - total_flagged

    # if the number of mines left to find is the same as the number of covered tiles, every covered tile should be a mine
    if mines_remaining == len(unknown_tiles):
        mine_tiles.update(unknown_tiles)

    return mine_tiles


def find_subset_moves(board):
    """Return (safe_tiles, mine_tiles), reusing derived subset groups.

    Existing flags are assumed correct. The input board is left unchanged.
    """
    constraints = _get_clue_constraints(board)
    if constraints is None:
        return set(), set()
    return _find_group_moves(constraints, allow_overlap=False) or (set(), set())


def find_overlap_moves(board):
    """Return certain moves from chained subset and partial-overlap deductions."""
    constraints = _get_clue_constraints(board)
    if constraints is None:
        return set(), set()
    return _find_group_moves(constraints, allow_overlap=True) or (set(), set())


def find_arrangement_moves(board, max_unknowns=15):
    """Return certain moves across all valid layouts in small connected groups.

    Groups with more than max_unknowns covered tiles are skipped. Existing
    flags are assumed correct, and the input board is left unchanged.
    """
    constraints = _get_clue_constraints(board)
    if constraints is None:
        return set(), set()
    return _find_arrangement_moves(constraints, max_unknowns) or (set(), set())


def find_advanced_moves(board, max_unknowns=15):
    """Combine chained group deductions and small-group arrangement searches."""
    constraints = _get_clue_constraints(board)
    if constraints is None:
        return set(), set()

    group_moves = _find_group_moves(constraints, allow_overlap=True)
    arrangement_moves = _find_arrangement_moves(constraints, max_unknowns)
    if group_moves is None or arrangement_moves is None:
        return set(), set()

    safe_tiles, mine_tiles = group_moves
    safe_tiles.update(arrangement_moves[0])
    mine_tiles.update(arrangement_moves[1])
    return safe_tiles, mine_tiles


def _get_clue_constraints(board):
    """Map each unknown-neighbor group to its remaining mine count.

    Return None if a clue contradicts the visible board or existing flags.
    """
    rows, columns = board.shape
    constraints = {}

    # Each clue gives an unknown-neighbor group and its remaining mine count.
    for row in range(rows):
        for col in range(columns):
            number = board[row, col]

            if number == reader.EMPTY:
                number = 0
            elif not 1 <= number <= 8:
                continue

            flagged_count = 0
            unknown_neighbors = set()

            for neighbor_row, neighbor_col in get_neighbors(board, row, col):
                neighbor = board[neighbor_row, neighbor_col]

                if neighbor == reader.FLAG:
                    flagged_count += 1
                elif neighbor == reader.UNKNOWN:
                    unknown_neighbors.add((neighbor_row, neighbor_col))

            remaining_mines = int(number) - flagged_count

            if not 0 <= remaining_mines <= len(unknown_neighbors):
                return None
            if not unknown_neighbors:
                continue

            group = frozenset(unknown_neighbors)
            if group in constraints and constraints[group] != remaining_mines:
                return None
            constraints[group] = remaining_mines

    return constraints


def _find_group_moves(constraints, allow_overlap, max_groups=512):
    """Keep derived groups for further comparisons, with a bounded group count."""
    groups = dict(constraints)
    pending = list(groups)
    group_limit = max(max_groups, len(groups))

    safe_tiles = set()
    mine_tiles = set()

    def add_group(tiles, mines):
        if not 0 <= mines <= len(tiles):
            return False
        if not tiles:
            return True
        if tiles in groups and groups[tiles] != mines:
            return False

        if mines == 0:
            safe_tiles.update(tiles)
        elif mines == len(tiles):
            mine_tiles.update(tiles)

        if tiles not in groups and len(groups) < group_limit:
            groups[tiles] = mines
            pending.append(tiles)
        return True

    while pending:
        group = pending.pop()
        count = groups[group]
        if not add_group(group, count):
            return None

        for other, other_count in list(groups.items()):
            if group < other:
                derived = [(other - group, other_count - count)]
            elif other < group:
                derived = [(group - other, count - other_count)]
            elif allow_overlap and group != other and group & other:
                shared = group & other
                group_only = group - other
                other_only = other - group

                # Both clues restrict how many mines their shared tiles can hold.
                minimum_shared = max(0, count - len(group_only),
                                     other_count - len(other_only))
                maximum_shared = min(len(shared), count, other_count)
                if minimum_shared > maximum_shared:
                    return None
                if minimum_shared != maximum_shared:
                    continue

                derived = [
                    (shared, minimum_shared),
                    (group_only, count - minimum_shared),
                    (other_only, other_count - minimum_shared),
                ]
            else:
                continue

            for tiles, mines in derived:
                if not add_group(tiles, mines):
                    return None

    if safe_tiles & mine_tiles:
        return None
    return safe_tiles, mine_tiles


def _constraint_components(constraints):
    """Split clues into independent groups connected by shared unknown tiles."""
    groups_by_tile = {}
    for group in constraints:
        for tile in group:
            groups_by_tile.setdefault(tile, []).append(group)

    remaining = set(constraints)
    while remaining:
        first = remaining.pop()
        component = {first: constraints[first]}
        tiles = set(first)
        pending = list(first)

        while pending:
            tile = pending.pop()
            for group in groups_by_tile[tile]:
                if group not in remaining:
                    continue
                remaining.remove(group)
                component[group] = constraints[group]
                new_tiles = group - tiles
                tiles.update(new_tiles)
                pending.extend(new_tiles)

        yield component, tiles


def _search_arrangements(constraints, tiles):
    """Intersect all valid layouts to find always-mined and always-safe tiles."""
    clues = list(constraints.items())
    groups_by_tile = {tile: [] for tile in tiles}
    for index, (group, _) in enumerate(clues):
        for tile in group:
            groups_by_tile[tile].append(index)

    # Start with tiles constrained by the most clues, to reject bad layouts sooner.
    ordered_tiles = sorted(tiles, key=lambda tile: (-len(groups_by_tile[tile]), tile))
    assigned_mines = [0] * len(clues)
    unassigned_tiles = [len(group) for group, _ in clues]
    placement = set()
    always_mines = set(tiles)
    possible_mines = set()
    solutions = 0

    def search(position):
        nonlocal solutions
        if position == len(ordered_tiles):
            solutions += 1
            always_mines.intersection_update(placement)
            possible_mines.update(placement)
            return

        tile = ordered_tiles[position]
        affected = groups_by_tile[tile]

        for is_mine in (0, 1):
            for index in affected:
                assigned_mines[index] += is_mine
                unassigned_tiles[index] -= 1

            # A partial layout is possible only if each clue can still be met.
            valid = all(
                assigned_mines[index] <= clues[index][1]
                <= assigned_mines[index] + unassigned_tiles[index]
                for index in affected
            )
            if valid:
                if is_mine:
                    placement.add(tile)
                search(position + 1)
                if is_mine:
                    placement.remove(tile)

            for index in affected:
                assigned_mines[index] -= is_mine
                unassigned_tiles[index] += 1

    search(0)
    if solutions == 0:
        return None
    return set(tiles) - possible_mines, always_mines


def _find_arrangement_moves(constraints, max_unknowns):
    if max_unknowns < 0:
        raise ValueError("max_unknowns must be zero or greater")

    safe_tiles = set()
    mine_tiles = set()
    for component, tiles in _constraint_components(constraints):
        if len(tiles) > max_unknowns:
            continue
        moves = _search_arrangements(component, tiles)
        if moves is None:
            return None
        safe_tiles.update(moves[0])
        mine_tiles.update(moves[1])

    return safe_tiles, mine_tiles

