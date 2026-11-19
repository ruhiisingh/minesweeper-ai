# Structuring
ai.py
  ├── owns the game and coordinates each turn
  ├── reader.py → returns only player(agent)-visible board information
  └── solver.py → finds moves using deterministic rules/patterns
  

# How to run
Ensuring python is installed in your system and present in your PATH, running `python ai.py` while located in `/Minesweeper/python-tkinter-minesweeper` should start an floating game instance.

# Python virtual Environment
Run these commands (While located in `/Minesweeper/python-tkinter-minesweeper`):
- `python -m venv .venv`
- Activate your virtual environment
    - Mac/Unix/Linux based users (depends on terminal shell):
        - `source /.venv/bin/activate`
        - `source /.venv/bin/activate.csh`
        - `source /.venv/bin/activate.fish`
    - Windows:
        - Run this while in powershell `/.venv/Scripts/activate`
- Install required packages (while using the venv)
    - `pip install -r requirements.txt`
