from pathlib import Path
import joblib
import reader
import solver

MODEL_PATH = Path(__file__).resolve().parent / "minesweeper_tree.joblib"

""" load decision tree """
def load_model():
    return joblib.load(str(MODEL_PATH))

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


