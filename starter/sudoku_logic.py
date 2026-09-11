import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def count_solutions(board, limit=2):
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return 0
    if any(
        cell not in range(EMPTY, SIZE + 1)
        for row in board
        for cell in row
    ):
        return 0

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value != EMPTY:
                board[row][col] = EMPTY
                valid = is_safe(board, row, col, value)
                board[row][col] = value
                if not valid:
                    return 0

    def search():
        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] != EMPTY:
                    continue
                candidates = [
                    candidate
                    for candidate in range(1, SIZE + 1)
                    if is_safe(board, row, col, candidate)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates
                    if len(candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            return 1

        row, col = best_cell
        solutions = 0
        for candidate in best_candidates:
            board[row][col] = candidate
            solutions += search()
            board[row][col] = EMPTY
            if solutions >= limit:
                return limit
        return solutions

    return search()

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    coordinates = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] != EMPTY
    ]
    random.shuffle(coordinates)
    removals_needed = len(coordinates) - clues

    if removals_needed < 0:
        raise ValueError("clues cannot exceed the number of filled cells")

    removals = 0
    for row, col in coordinates:
        if removals == removals_needed:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            removals += 1
        else:
            board[row][col] = value

    if removals != removals_needed:
        raise ValueError("unable to generate a puzzle with the requested clues")

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
