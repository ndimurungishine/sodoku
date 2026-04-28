"""
SUDOKU GAME - Tkinter GUI
====================================
Data Structures & Algorithms Demonstrated (Exclusive of Arrays):
  1. Stack          - Undo/Redo move history
  2. Queue (deque)  - Hint system (BFS-based cell traversal)
  3. Dictionary     - Board state, cell metadata, candidate tracking
  4. Set            - Constraint validation (row/col/box conflicts)
  5. Linked List    - Move history chain
  6. Backtracking   - Puzzle solver algorithm
  7. Constraint Propagation - Candidate elimination during generation

Run: python soduko.py
"""

import random
import copy
import time
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque




# 1. LINKED LIST — Move History Chain

class MoveNode:
    """A single node in a doubly-linked move history list."""
    def __init__(self, row, col, old_value, new_value):
        self.row = row
        self.col = col
        self.old_value = old_value
        self.new_value = new_value
        self.prev = None  # points to the node before this move (previous move)
        self.next = None # points to the node after this move (next move if we redo)

    def __repr__(self):
        return (f"Move({self.row},{self.col}: "
                f"{self.old_value}→{self.new_value})")


class MoveLinkedList:
    """Doubly-linked list of moves to support undo/redo."""
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0
    def push(self, row, col, old_val, new_val):
        node = MoveNode(row, col, old_val, new_val)
        if self.current:
            node.prev = self.current # the new node remembers what came before it
            self.current.next = node # the old node now points forward to the new node
        self.current = node
        if not self.head:
            self.head = node
        self.size += 1

    def undo(self):
        if not self.current:
            return None
        node = self.current
        self.current = self.current.prev
        self.size -= 1
        return node

    def redo(self):
        if self.current and self.current.next:
            self.current = self.current.next
            self.size += 1
            return self.current
        return None

    def is_empty(self):
        return self.current is None



# 2. STACK — Undo/Redo using the Linked List

class UndoStack:
    def __init__(self):
        self._list = MoveLinkedList()

    def push(self, row, col, old_val, new_val):
        self._list.push(row, col, old_val, new_val) #add to the top of the stack (linked list)

    def pop(self):
        return self._list.undo() #remove from the top of the stack (linked list) 

    def redo(self):
        return self._list.redo()

    def peek(self):
        return self._list.current

    def is_empty(self):
        return self._list.is_empty()

    def size(self):
        return self._list.size


# ─────────────────────────────────────────────
# 3. DICTIONARY + SET — Board & Constraint Engine
# ─────────────────────────────────────────────
class SudokuBoard:
    """
    Board stored as a dict: {(row, col): value}
    Constraints tracked with sets per row/col/box.
    """
    def __init__(self):
        self.cells: dict = {}
        self.given: set = set()

        self.row_used:  dict = {r: set() for r in range(9)}
        self.col_used:  dict = {c: set() for c in range(9)}
        self.box_used:  dict = {b: set() for b in range(9)}

        for r in range(9):
            for c in range(9):
                self.cells[(r, c)] = 0

    @staticmethod
    def box_index(row, col):
        return (row // 3) * 3 + (col // 3)

    def place(self, row, col, value, is_given=False):
        old = self.cells.get((row, col), 0)
        if old != 0:
            self.row_used[row].discard(old)
            self.col_used[col].discard(old)
            self.box_used[self.box_index(row, col)].discard(old)

        self.cells[(row, col)] = value
        if value != 0:
            self.row_used[row].add(value)
            self.col_used[col].add(value)
            self.box_used[self.box_index(row, col)].add(value)

        if is_given:
            self.given.add((row, col))

    def clear(self, row, col):
        self.place(row, col, 0)

    def is_valid_placement(self, row, col, value):
        if value in self.row_used[row]:
            return False
        if value in self.col_used[col]:
            return False
        if value in self.box_used[self.box_index(row, col)]:
            return False
        return True

    def candidates(self, row, col):
        if self.cells[(row, col)] != 0:
            return set()
        used = (self.row_used[row] |
                self.col_used[col] |
                self.box_used[self.box_index(row, col)])
        return set(range(1, 10)) - used

    def is_complete(self):
        return all(v != 0 for v in self.cells.values())

    def is_solved_correctly(self):
        if not self.is_complete():
            return False
        for r in range(9):
            if self.row_used[r] != set(range(1, 10)):
                return False
        for c in range(9):
            if self.col_used[c] != set(range(1, 10)):
                return False
        for b in range(9):
            if self.box_used[b] != set(range(1, 10)):
                return False
        return True

    def copy(self):
        new_board = SudokuBoard()
        for pos, val in self.cells.items():
            new_board.cells[pos] = val
        new_board.given = set(self.given)
        for r in range(9):
            new_board.row_used[r] = set(self.row_used[r])
        for c in range(9):
            new_board.col_used[c] = set(self.col_used[c])
        for b in range(9):
            new_board.box_used[b] = set(self.box_used[b])
        return new_board


# ─────────────────────────────────────────────
# 4. BACKTRACKING ALGORITHM — Solver
# ─────────────────────────────────────────────
class SudokuSolver:
    def __init__(self, board: SudokuBoard):
        self.board = board.copy()
        self.steps = 0

    def _select_cell(self):
        min_count = 10
        best_cell = None
        for r in range(9):
            for c in range(9):
                if self.board.cells[(r, c)] == 0:
                    cands = self.board.candidates(r, c)
                    if len(cands) < min_count:
                        min_count = len(cands)
                        best_cell = (r, c, cands)
                        if min_count == 1:
                            return best_cell
        return best_cell

    def solve(self):
        self.steps += 1
        cell = self._select_cell()
        if cell is None:
            return True
        row, col, candidates = cell
        if not candidates:
            return False
        for digit in candidates:
            self.board.place(row, col, digit)
            if self.solve():
                return True
            self.board.clear(row, col)
        return False

    def get_solution(self):
        if self.solve():
            return self.board
        return None


# ─────────────────────────────────────────────
# 5. CONSTRAINT PROPAGATION — Puzzle Generator
# ─────────────────────────────────────────────
class SudokuGenerator:
    def __init__(self, difficulty="medium"):
        self.clue_counts = {"easy": 36, "medium": 28, "hard": 22}
        self.clues = self.clue_counts.get(difficulty, 28)

    def _fill_diagonal_boxes(self, board: SudokuBoard):
        for box in range(3):
            digits = list(range(1, 10))
            random.shuffle(digits)
            idx = 0
            for r in range(box * 3, box * 3 + 3):
                for c in range(box * 3, box * 3 + 3):
                    board.place(r, c, digits[idx], is_given=False)
                    idx += 1

    def generate(self):
        board = SudokuBoard()
        self._fill_diagonal_boxes(board)
        solver = SudokuSolver(board)
        solution = solver.get_solution()
        if not solution:
            return self.generate()

        puzzle = solution.copy()
        positions = list(puzzle.cells.keys())
        random.shuffle(positions)

        removed = 0
        target_remove = 81 - self.clues

        for pos in positions:
            if removed >= target_remove:
                break
            row, col = pos
            backup = puzzle.cells[pos]
            puzzle.clear(row, col)
            test_solver = SudokuSolver(puzzle)
            test_solution = test_solver.get_solution()
            if test_solution and test_solution.cells == solution.cells:
                removed += 1
            else:
                puzzle.place(row, col, backup)

        for pos, val in puzzle.cells.items():
            if val != 0:
                puzzle.given.add(pos)

        return puzzle, solution


# ─────────────────────────────────────────────
# 6. QUEUE — Hint System (BFS)
# ─────────────────────────────────────────────
class HintSystem:
    def __init__(self, board: SudokuBoard, solution: SudokuBoard):
        self.board = board
        self.solution = solution

    def get_hint(self):
        queue = deque()    #create am empty queue to store the empty cells
        visited = set() 
        for r in range(9):
            for c in range(9):
                if self.board.cells[(r, c)] == 0:
                    queue.append((r, c))    # enqueue empty cell(add empty cell to back)
                    visited.add((r, c))

        best = None
        min_cands = 10
        while queue:                                                     #(0,2)=>cands={1,3,5,} 3 options
            r, c = queue.popleft() #take or removes from the front       #(1,0)=>cands={1,2,4,5,6,7,8} 7 options
            cands = self.board.candidates(r, c)                        #(2,2)=>cands={4} 1 option
            if len(cands) < min_cands:    #track the cell with fewest candidates)                
                min_cands = len(cands)
                correct = self.solution.cells[(r, c)]
                best = (r, c, correct)

        return best


# ─────────────────────────────────────────────
# 7. TKINTER GUI
# ─────────────────────────────────────────────
class SudokuGUI:
    # Colors
    BG           = "#f5f4f0"
    CELL_BG      = "#ffffff"
    GIVEN_FG     = "#1a1a1a"
    PLAYER_FG    = "#185fa5"
    CONFLICT_FG  = "#a32d2d"
    CONFLICT_BG  = "#fde8e8"
    SELECTED_BG  = "#daeaf7"
    HIGHLIGHT_BG = "#f0f0ec"
    HINT_BG      = "#e6f5d0"
    HINT_FG      = "#3b6d11"
    BTN_BG       = "#ffffff"
    BTN_FG       = "#555555"
    BORDER_DARK  = "#333333"
    BORDER_LIGHT = "#d5d3ce"

    CELL_SIZE   = 58
    FONT_GIVEN  = ("Helvetica", 20, "bold")
    FONT_PLAYER = ("Helvetica", 20)
    FONT_NOTE   = ("Helvetica", 7)
    FONT_BTN    = ("Helvetica", 11)
    FONT_STATUS = ("Helvetica", 11)

    CELL_SIZE   = 40

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku — Data Structures Edition")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.difficulty = tk.StringVar(value="medium")
        self.selected   = None   # (row, col)
        self.note_mode  = False
        self.game_over  = False
        self.moves      = 0
        self.hints_used = 0
        self.start_time = None
        self._timer_id  = None

        self.board    = None
        self.solution = None
        self.undo_stack  = UndoStack()
        self.hint_system = None
        self.notes    = {}       # dict: (r,c) -> set of candidate digits

        self._build_ui()
        self._new_game()

    # ── UI CONSTRUCTION ──────────────────────
    def _build_ui(self):
        pad = dict(padx=12, pady=8)

        # Title
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill="x", **pad)
        tk.Label(title_frame, text="Sudoku", font=("Helvetica", 20, "bold"),
                 bg=self.BG, fg="#1a1a1a").pack(side="left")

        # Difficulty row
        diff_frame = tk.Frame(self.root, bg=self.BG)
        diff_frame.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(diff_frame, text="Difficulty:", font=self.FONT_STATUS,
                 bg=self.BG, fg="#888").pack(side="left", padx=(0, 8))
        for d in ("easy", "medium", "hard"):
            tk.Radiobutton(diff_frame, text=d.capitalize(),
                           variable=self.difficulty, value=d,
                           font=self.FONT_STATUS, bg=self.BG,
                           command=self._new_game).pack(side="left", padx=4)

        # Stats row
        stats_frame = tk.Frame(self.root, bg=self.BG)
        stats_frame.pack(fill="x", padx=12, pady=(0, 8))
        self.lbl_timer = tk.Label(stats_frame, text="Time: 0:00",
                                  font=self.FONT_STATUS, bg=self.BG, fg="#555")
        self.lbl_timer.pack(side="left", padx=(0, 16))
        self.lbl_moves = tk.Label(stats_frame, text="Moves: 0",
                                  font=self.FONT_STATUS, bg=self.BG, fg="#555")
        self.lbl_moves.pack(side="left", padx=(0, 16))
        self.lbl_hints = tk.Label(stats_frame, text="Hints: 0",
                                  font=self.FONT_STATUS, bg=self.BG, fg="#555")
        self.lbl_hints.pack(side="left")

        # Canvas board
        board_size = self.CELL_SIZE * 9 + 4
        self.canvas = tk.Canvas(self.root, width=board_size, height=board_size,
                                bg=self.CELL_BG, highlightthickness=0)
        self.canvas.pack(padx=12, pady=(0, 8))
        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Key>", self._on_key)

        # Number pad
        pad_frame = tk.Frame(self.root, bg=self.BG)
        pad_frame.pack(padx=12, pady=(0, 8))
        for n in range(1, 10):
            btn = tk.Button(pad_frame, text=str(n), width=3, height=1,
                            font=("Helvetica", 14, "bold"),
                            bg=self.BTN_BG, fg="#1a1a1a",
                            relief="groove", cursor="hand2",
                            command=lambda v=n: self._input(v))
            btn.grid(row=0, column=n-1, padx=2, pady=2)
        tk.Button(pad_frame, text="Erase", width=6,
                  font=self.FONT_BTN, bg=self.BTN_BG, fg="#888",
                  relief="groove", cursor="hand2",
                  command=lambda: self._input(0)).grid(
                      row=0, column=9, padx=2, pady=2)

        # Action buttons
        act_frame = tk.Frame(self.root, bg=self.BG)
        act_frame.pack(padx=12, pady=(0, 6))
        actions = [
            ("↩ Undo",     self._undo,      "#555"),
            ("↪ Redo",     self._redo,      "#555"),
            ("💡 Hint",    self._hint,      "#185fa5"),
            ("✏ Notes",   self._toggle_notes, "#555"),
            ("⚡ Solve",   self._auto_solve, "#a32d2d"),
            ("🎲 New Game",self._new_game,   "#1a1a1a"),
        ]
        for i, (label, cmd, fg) in enumerate(actions):
            btn = tk.Button(act_frame, text=label, width=10,
                            font=self.FONT_BTN, bg=self.BTN_BG, fg=fg,
                            relief="groove", cursor="hand2", command=cmd)
            btn.grid(row=i//3, column=i%3, padx=4, pady=3, sticky="ew")
        self.note_btn = act_frame.grid_slaves(row=1, column=1)[0]

        # Status bar
        self.lbl_status = tk.Label(self.root, text="", font=self.FONT_STATUS,
                                   bg=self.BG, fg="#3b6d11")
        self.lbl_status.pack(pady=(0, 4))

        # DS info bar
        ds_text = ("Stack · Linked List · Queue (BFS) · "
                   "Dictionary · Set · Backtracking + MRV")
        tk.Label(self.root, text=ds_text, font=("Helvetica", 9),
                 bg=self.BG, fg="#aaa").pack(pady=(0, 10))

    # ── GAME LOGIC ───────────────────────────
    def _new_game(self):
        self._stop_timer()
        self.game_over   = False
        self.selected    = None
        self.moves       = 0
        self.hints_used  = 0
        self.notes       = {}
        self.undo_stack  = UndoStack()
        self.lbl_status.config(text="Generating puzzle...", fg="#888")
        self.root.update()

        gen = SudokuGenerator(self.difficulty.get())
        self.board, self.solution = gen.generate()
        self.hint_system = HintSystem(self.board, self.solution)

        self.lbl_moves.config(text="Moves: 0")
        self.lbl_hints.config(text="Hints: 0")
        self.lbl_status.config(text="")
        self._draw_board()
        self._start_timer()

    def _input(self, value):
        if self.selected is None or self.game_over:
            return
        r, c = self.selected
        if (r, c) in self.board.given:
            self._status("Cannot change a given cell.", error=True)
            return

        if self.note_mode and value > 0:
            key = (r, c)
            if key not in self.notes:
                self.notes[key] = set()
            if value in self.notes[key]:
                self.notes[key].discard(value)
            else:
                self.notes[key].add(value)
            self._draw_board()
            return

        if value > 0 and not self.board.is_valid_placement(r, c, value):
            self._status(f"Conflict! {value} already in this row/col/box.", error=True)
            # still place it (show in red) — comment out if you prefer strict mode
        old_val = self.board.cells[(r, c)]
        self.board.place(r, c, value)
        self.notes[(r, c)] = set()
        self.undo_stack.push(r, c, old_val, value)
        self.moves += 1
        self.lbl_moves.config(text=f"Moves: {self.moves}")
        self._status("")
        self._draw_board()

        if self.board.is_solved_correctly():
            self._win()

    def _undo(self):
        move = self.undo_stack.pop()
        if not move:
            self._status("Nothing to undo.")
            return
        self.board.place(move.row, move.col, move.old_value)
        self.selected = (move.row, move.col)
        self._draw_board()
        self._status("")

    def _redo(self):
        move = self.undo_stack.redo()
        if not move:
            self._status("Nothing to redo.")
            return
        self.board.place(move.row, move.col, move.new_value)
        self.selected = (move.row, move.col)
        self._draw_board()
        self._status("")

    def _hint(self):
        if self.game_over:
            return
        h = self.hint_system.get_hint()
        if not h:
            self._status("No empty cells remaining!")
            return
        row, col, digit = h
        self.hints_used += 1
        self.lbl_hints.config(text=f"Hints: {self.hints_used}")
        old_val = self.board.cells[(row, col)]
        self.board.place(row, col, digit)
        self.notes[(row, col)] = set()
        self.undo_stack.push(row, col, old_val, digit)
        self.moves += 1
        self.lbl_moves.config(text=f"Moves: {self.moves}")
        self.selected = (row, col)
        self._draw_board(hint_cell=(row, col))
        self._status(f"Hint: placed {digit} at row {row+1}, col {col+1}")
        if self.board.is_solved_correctly():
            self._win()

    def _auto_solve(self):
        if self.game_over:
            return
        solver = SudokuSolver(self.board)
        solved = solver.get_solution()
        if solved:
            self.board = solved
            self.selected = None
            self.game_over = True
            self._stop_timer()
            self._draw_board()
            self._status(f"Auto-solved in {solver.steps} recursive steps!")
        else:
            self._status("No solution found from current state.", error=True)

    def _toggle_notes(self):
        self.note_mode = not self.note_mode
        if self.note_mode:
            self.note_btn.config(text="✏ Notes ON", fg="#185fa5", bg="#eaf3fb")
        else:
            self.note_btn.config(text="✏ Notes", fg="#555", bg=self.BTN_BG)

    def _win(self):
        self.game_over = True
        self._stop_timer()
        elapsed = self.lbl_timer.cget("text").replace("Time: ", "")
        self._draw_board()
        self._status(f"🏆 Solved! {elapsed} | Moves: {self.moves} | Hints: {self.hints_used}")
        messagebox.showinfo("Congratulations!",
                            f"Puzzle solved!\n\nTime: {elapsed}\n"
                            f"Moves: {self.moves}\nHints used: {self.hints_used}")

    # ── DRAWING ──────────────────────────────
    def _draw_board(self, hint_cell=None):
        self.canvas.delete("all")
        cs = self.CELL_SIZE
        offset = 2  # border offset

        for r in range(9):
            for c in range(9):
                x0 = offset + c * cs
                y0 = offset + r * cs
                x1 = x0 + cs
                y1 = y0 + cs

                # Cell background
                pos = (r, c)
                bg = self.CELL_BG
                val = self.board.cells[pos]
                is_given = pos in self.board.given
                conflict = (val != 0 and not is_given and
                            not self.board.is_valid_placement(r, c, val))

                if hint_cell == pos:
                    bg = self.HINT_BG
                elif self.selected == pos:
                    bg = self.SELECTED_BG
                elif self.selected:
                    sr, sc = self.selected
                    if (sr == r or sc == c or
                            SudokuBoard.box_index(sr, sc) == SudokuBoard.box_index(r, c)):
                        bg = self.HIGHLIGHT_BG
                if conflict:
                    bg = self.CONFLICT_BG

                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=bg, outline="")

                # Cell value
                if val != 0:
                    if is_given:
                        fg = self.GIVEN_FG
                        font = self.FONT_GIVEN
                    elif hint_cell == pos:
                        fg = self.HINT_FG
                        font = self.FONT_PLAYER
                    elif conflict:
                        fg = self.CONFLICT_FG
                        font = self.FONT_PLAYER
                    else:
                        fg = self.PLAYER_FG
                        font = self.FONT_PLAYER
                    self.canvas.create_text(
                        x0 + cs // 2, y0 + cs // 2,
                        text=str(val), font=font, fill=fg)

                # Candidate notes
                elif pos in self.notes and self.notes[pos]:
                    for n in self.notes[pos]:
                        nr = (n - 1) // 3
                        nc = (n - 1) % 3
                        nx = x0 + nc * (cs // 3) + cs // 6
                        ny = y0 + nr * (cs // 3) + cs // 6
                        self.canvas.create_text(nx, ny, text=str(n),
                                                font=self.FONT_NOTE, fill="#aaa")

        # Grid lines
        for i in range(10):
            lw = 2.5 if i % 3 == 0 else 0.5
            color = self.BORDER_DARK if i % 3 == 0 else self.BORDER_LIGHT
            x = offset + i * cs
            y = offset + i * cs
            self.canvas.create_line(x, offset, x, offset + 9 * cs,
                                    width=lw, fill=color)
            self.canvas.create_line(offset, y, offset + 9 * cs, y,
                                    width=lw, fill=color)

    # ── EVENTS ───────────────────────────────
    def _on_click(self, event):
        cs = self.CELL_SIZE
        offset = 2
        c = (event.x - offset) // cs
        r = (event.y - offset) // cs
        if 0 <= r < 9 and 0 <= c < 9:
            self.selected = (r, c)
            self._draw_board()

    def _on_key(self, event):
        key = event.keysym
        if key in [str(n) for n in range(1, 10)]:
            self._input(int(key))
        elif key in ("BackSpace", "Delete", "0"):
            self._input(0)
        elif key == "z" and (event.state & 0x4):   # Ctrl+Z
            self._undo()
        elif key == "y" and (event.state & 0x4):   # Ctrl+Y
            self._redo()
        elif self.selected:
            r, c = self.selected
            moves = {"Up": (-1,0), "Down": (1,0), "Left": (0,-1), "Right": (0,1)}
            if key in moves:
                dr, dc = moves[key]
                nr = max(0, min(8, r + dr))
                nc = max(0, min(8, c + dc))
                self.selected = (nr, nc)
                self._draw_board()

    # ── TIMER ────────────────────────────────
    def _start_timer(self):
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if self.game_over:
            return
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.lbl_timer.config(text=f"Time: {m}:{s:02d}")
        self._timer_id = self.root.after(1000, self._tick)

    def _stop_timer(self):
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    # ── STATUS ───────────────────────────────
    def _status(self, text, error=False):
        color = "#a32d2d" if error else "#3b6d11"
        self.lbl_status.config(text=text, fg=color)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()