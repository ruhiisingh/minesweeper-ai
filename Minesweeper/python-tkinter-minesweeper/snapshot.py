from pathlib import Path
from uuid import uuid4

import numpy as np
import reader


def save_snapshot(visible_board, tiles):
    """Save boards with at least two revealed tiles, or return None."""
    revealed = (
        ((visible_board >= 1) & (visible_board <= 8))
        | (visible_board == reader.EMPTY)
    )
    if np.count_nonzero(revealed) <= 1:
        return None

    rows, columns = visible_board.shape

    # Ground truth for training labels, separate from the visible board.
    mine_mask = np.array(
        [
            [tiles[row][column]["isMine"] for column in range(columns)]
            for row in range(rows)
        ],
        dtype=bool,
    )

    directory = Path(__file__).resolve().parent / "snapshots"
    directory.mkdir(exist_ok=True)

    path = directory / f"{uuid4().hex}.npz"

    np.savez_compressed(
        path,
        visible_board=visible_board,
        mine_mask=mine_mask,
        total_mines=mine_mask.sum(),
    )

    return path
