from pathlib import Path
import joblib
import reader
import solver

MODEL_PATH = Path(__file__).resolve().parent / "minesweeper_tree.joblib"

""" load decision tree """
def load_model(path=MODEL_PATH):
    return joblib.load(str(path))

""" Return prob that tile has a mine """
def get_mine_probability(model, attributes):
    probabilities = model.predict_proba([attributes])[0]

    for label, probability in zip(model.classes_, probabilities):
        if int(label) == 1:
            return float(probability)

    return 0.0

def get_candidate_tiles(board):

    rows, cols = board.shape

    for row in range(rows):
        for col in range(cols):

            if board[row, col] != reader.UNKNOWN:
                continue

            attributes = solver.get_tree_attributes(board, row, col)

            if all(value == reader.UNKNOWN or value == solver.EDGE for value in attributes):
                continue

            yield row, col, attributes

def find_mines(board, model, threshold = 0.90):

    tiles_to_flag = set()

    for row, col, attributes in get_candidate_tiles(board):
        prob = get_mine_probability(model, attributes)

        if prob >= threshold:
            tiles_to_flag.add((row, col))

    return tiles_to_flag

def find_safe_tiles(board, model, threshold = 0.10):
    safe_tiles = set()

    for row, col, attributes in get_candidate_tiles(board):
        prob = get_mine_probability(model, attributes)

        if prob <= threshold:
            safe_tiles.add((row, col))

    return safe_tiles


def find_safest_tile(board, model):
    safest_tile = None
    lowest_prob = 1.0

    for row, col, attributes in get_candidate_tiles(board):
        prob = get_mine_probability(model, attributes)

        if prob < lowest_prob:
            lowest_prob = prob
            safest_tile = (row, col)
    
    return safest_tile


def choose_move(board, model, total_mines):
    """Return (source, row, column), or None, using only the visible board."""
    if (board == reader.UNKNOWN).all():
        return "opening", 0, 0

    solver_mines = solver.find_mines(board)
    solver_mines.update(solver.find_mines_from_total(board, total_mines))
    solver_safe_tiles = solver.find_safe_tiles(board)
    solver_safe_tiles.update(solver.find_safe_tiles_from_total(board, total_mines))

    # Try more expensive comparisons only when the simple rules find nothing.
    if not solver_mines and not solver_safe_tiles:
        advanced_safe, advanced_mines = solver.find_advanced_moves(board)
        solver_safe_tiles.update(advanced_safe)
        solver_mines.update(advanced_mines)

    if solver_mines:
        row, column = min(solver_mines)
        return "flag", row, column

    if solver_safe_tiles:
        row, column = min(solver_safe_tiles)
        return "safe", row, column

    safest_tile = find_safest_tile(board, model)
    if safest_tile is None:
        return None

    row, column = safest_tile
    return "tree", row, column


