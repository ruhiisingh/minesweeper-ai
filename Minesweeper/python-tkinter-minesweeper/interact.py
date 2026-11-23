import minesweeper as ms


"""
Since ai.py 'owns' the game instance, the tkinter interactions
can just be handled without needing any other external libraries
since the event handlers for an button press, can just be called
here for the ai.

Massive win, since any window size & scaling is pretty much covered.
"""


# Left click
"""
if statement checks if tile is default (untouched).
If tile pressed ignore, otherwise press
"""
def reveal(game, row, column):
    tile = game.tiles[row][column]

    if tile["state"] != ms.STATE_DEFAULT:
        return
    game.onClick(tile)

# Right click
"""
If tile is default (untouched)
place flag here, requires logic being handled elsewhere.
Since this file is just for right + left click
"""
def flag(game, row, column):
    tile = game.tiles[row][column]

    if tile["state"] == ms.STATE_DEFAULT:
        game.onRightClick(tile)
