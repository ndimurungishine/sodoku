## Sudoku Game

A fully playable Sudoku game with a Tkinter GUI, built 
using 7 Data Structures & Algorithms (no arrays used).

## Data Structures Used
1. **Stack** - Undo/Redo move history (UndoStack)
2. **Linked List** - Move history chain (MoveLinkedList)
3. **Dictionary** - Board state and candidate tracking (SudokuBoard)
4. **Set** - Constraint validation for rows, columns and boxes
5. **Queue (deque)** - BFS-based hint system (HintSystem)
6. **Backtracking** - Puzzle solver algorithm (SudokuSolver)
7. **Constraint Propagation** - Candidate elimination during generation

## Features
- Playable 9x9 Sudoku board
- Undo (Ctrl+Z) and Redo (Ctrl+Y)
- Hint system
- Auto-solve
- Notes/candidate mode
- Conflict highlighting
- Timer and move counter
- Multiple difficulty levels

## How to Run
1. Make sure Python is installed
2. Run: python sodokugame.py

## Requirements
- Python 3.x
- Tkinter (built into Python)
