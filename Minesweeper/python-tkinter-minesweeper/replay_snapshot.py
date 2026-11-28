"""Evaluate the tree agent against every saved stalled game, without a GUI."""

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from pickle import UnpicklingError
from zipfile import BadZipFile

import numpy as np

import reader
import solver
import tree_solver


BASE_DIRECTORY = Path(__file__).resolve().parent
SNAPSHOT_DIRECTORY = BASE_DIRECTORY / "snapshots"


@dataclass(frozen=True)
class ReplayResult:
    status: str
    moves: int = 0
    tree_moves: int = 0
    detail: str = ""


def neighbor_counts(mine_mask):
    counts = np.zeros(mine_mask.shape, dtype=np.int8)
    for row, column in np.ndindex(mine_mask.shape):
        counts[row, column] = sum(
            int(mine_mask[r, c])
            for r, c in solver.get_neighbors(mine_mask, row, column)
        )
    return counts


def load_snapshot(path):
    """Validate and restore the exact visible position and simulator mine mask."""
    with np.load(path, allow_pickle=False) as data:
        if not {"visible_board", "mine_mask", "total_mines"} <= set(data.files):
            raise ValueError("Snapshot needs visible_board, mine_mask, and total_mines.")
        board = data["visible_board"]
        mine_mask = data["mine_mask"]
        total_mines = data["total_mines"]

    if board.ndim != 2 or not all(board.shape) or mine_mask.shape != board.shape:
        raise ValueError("Snapshot boards must be nonempty, matching 2D arrays.")
    if not np.issubdtype(board.dtype, np.integer) or not np.isin(board, range(11)).all():
        raise ValueError("Visible board contains unsupported tile values.")
    if not np.isin(mine_mask, (0, 1)).all():
        raise ValueError("Mine mask must contain only boolean or 0/1 values.")

    board = board.astype(np.int8, copy=True)
    mine_mask = mine_mask.astype(bool, copy=True)
    if total_mines.shape != () or total_mines.item() != int(mine_mask.sum()):
        raise ValueError("Snapshot total_mines does not match its mine mask.")

    revealed = ((board >= 1) & (board <= 8)) | (board == reader.EMPTY)
    if np.any(revealed & mine_mask):
        raise ValueError("An ongoing snapshot cannot have a revealed mine.")
    if np.any((board == reader.FLAG) & ~mine_mask):
        raise ValueError("Replay rules require existing flags to be correct.")
    clues = np.where(board == reader.EMPTY, 0, board)
    if np.any(revealed & (clues != neighbor_counts(mine_mask))):
        raise ValueError("Visible clues do not match the saved mine layout.")
    return board, mine_mask


def reveal_tile(board, counts, row, column):
    """Reveal a safe tile, expanding zeroes without opening flagged cells."""
    pending = deque([(row, column)])
    while pending:
        row, column = pending.popleft()
        if board[row, column] != reader.UNKNOWN:
            continue
        count = counts[row, column]
        board[row, column] = reader.EMPTY if count == 0 else count
        if count == 0:
            pending.extend(solver.get_neighbors(board, row, column))


def replay_game(board, mine_mask, model):
    """Play one position using exactly the same move policy as tree_ai.py.

    Hidden mines belong only to the simulator: they determine click outcomes,
    revealed clues, and whether all safe cells have been opened.
    """
    board = board.copy()
    counts = neighbor_counts(mine_mask)
    total_mines = int(mine_mask.sum())
    moves = 0
    tree_moves = 0

    while True:
        revealed = ((board >= 1) & (board <= 8)) | (board == reader.EMPTY)
        if np.all(revealed | mine_mask):
            return ReplayResult("completed", moves, tree_moves)

        decision = tree_solver.choose_move(board, model, total_mines)
        if decision is None:
            return ReplayResult("stalled", moves, tree_moves, "No move available.")
        source, row, column = decision
        if (
            source not in ("opening", "flag", "safe", "tree")
            or not (0 <= row < board.shape[0] and 0 <= column < board.shape[1])
            or board[row, column] != reader.UNKNOWN
        ):
            return ReplayResult("stalled", moves, tree_moves, "Agent selected an invalid or unchanged tile.")

        # Each action consumes at least one covered tile, so replay cannot loop.
        moves += 1
        tree_moves += int(source == "tree")
        if source == "flag":
            board[row, column] = reader.FLAG
        elif mine_mask[row, column]:
            return ReplayResult("lost", moves, tree_moves, f"Mine revealed at {(row, column)}.")
        else:
            reveal_tile(board, counts, row, column)


def evaluate_snapshots(paths, model):
    """Attempt each file once; invalid snapshots stay in the total as errors."""
    for path in paths:
        try:
            board, mine_mask = load_snapshot(path)
            result = replay_game(board, mine_mask, model)
        except (OSError, ValueError, KeyError, EOFError, BadZipFile) as error:
            result = ReplayResult("error", detail=str(error))
        yield path, result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshots", type=Path, default=SNAPSHOT_DIRECTORY,
        help="Directory of saved .npz games (default: snapshots/ next to this script).",
    )
    parser.add_argument(
        "--model", type=Path, default=tree_solver.MODEL_PATH,
        help="Trained decision-tree file (default: minesweeper_tree.joblib).",
    )
    args = parser.parse_args(argv)
    if not args.snapshots.is_dir():
        parser.error(f"Snapshot directory not found: {args.snapshots}")
    paths = sorted(args.snapshots.glob("*.npz"))
    if not paths:
        parser.error(f"No snapshots found in {args.snapshots}.")

    try:
        model = tree_solver.load_model(args.model)
    except FileNotFoundError:
        parser.error(f"Trained model not found: {args.model}. Run python train_tree.py first, or use --model.")
    except (OSError, ValueError, ImportError, EOFError, UnpicklingError) as error:
        parser.error(f"Could not load trained model: {error}")

    outcomes = Counter()
    for index, (path, result) in enumerate(evaluate_snapshots(paths, model), 1):
        outcomes[result.status] += 1
        detail = f" {result.detail}" if result.detail else ""
        print(
            f"[{index}/{len(paths)}] {path.name}: {result.status.upper()} "
            f"({result.moves} moves, {result.tree_moves} tree guesses).{detail}"
        )

    completed = outcomes["completed"]
    total = len(paths)
    print(f"\nStalled games completed: {completed}/{total} ({completed / total:.1%})")
    print(
        f"Lost: {outcomes['lost']} | Still stalled: {outcomes['stalled']} "
        f"| Errors: {outcomes['error']}"
    )
    return outcomes


if __name__ == "__main__":
    main()
