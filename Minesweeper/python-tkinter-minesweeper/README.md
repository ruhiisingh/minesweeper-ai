# Structuring
ai.py                  -> creates the game and schedules turns  
└── solver.py          -> pattern/rule logic handling  
    ├── reader.py      -> reads the visible board  
    └── interact.py    -> flags or reveals a tile

`tree_ai.py` uses the same local, total-mine-count, and advanced rules as
`ai.py`, then asks the trained decision tree for a reveal only when those
rules find no move.

# Evaluate the tree agent on stalled games

`replay_snapshot.py` attempts every `.npz` game in `snapshots/`, once each,
without opening a window. It resumes where the rule based agent failed.

```sh
# Create the trained model first, if minesweeper_tree.joblib does not exist.
python train_tree.py

# Evaluate all saved stalled games with the current trained model.
python replay_snapshot.py

# Optionally select a different snapshot directory or trained model.
python replay_snapshot.py --snapshots snapshots --model minesweeper_tree.joblib
```

Requires NumPy, joblib, and scikit-learn, as used by the existing tree agent.
Tkinter and a display are not needed for batch evaluation. 

Each game is reported as `COMPLETED`, `LOST`, `STALLED`, or `ERROR`. The final
summary reports **Stalled games completed: completed/total (percentage)**,
followed by loss, remaining-stall, and error counts. The total includes every
`.npz` file in the selected directory, even invalid snapshots, so failed loads
do not inflate the completion rate.
Just a benchmark, no saved data is returned.
