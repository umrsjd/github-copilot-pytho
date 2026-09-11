import random

import sudoku_logic


def test_create_empty_board_returns_nine_by_nine_zero_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_is_independent_of_original():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 7

    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 3

    assert board[0][0] == 7
    assert copied_board[0][0] == 3


def test_is_safe_rejects_number_already_in_row():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 4, 5)
    assert sudoku_logic.is_safe(board, 0, 4, 6)


def test_is_safe_rejects_number_already_in_column():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 4, 0, 5)
    assert sudoku_logic.is_safe(board, 4, 0, 6)


def test_is_safe_rejects_number_already_in_three_by_three_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 2, 2, 5)
    assert sudoku_logic.is_safe(board, 2, 2, 6)


def test_fill_board_generates_a_complete_board():
    random.seed(0)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert all(
        cell in range(1, sudoku_logic.SIZE + 1)
        for row in board
        for cell in row
    )


def test_remove_cells_removes_requested_number_of_cells():
    random.seed(0)
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, clues=35)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 35


def test_generate_puzzle_has_requested_clue_count():
    random.seed(0)

    puzzle, _ = sudoku_logic.generate_puzzle(clues=40)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40


def test_generate_puzzle_returns_matching_dimensions_and_valid_values():
    random.seed(0)

    puzzle, solution = sudoku_logic.generate_puzzle()

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert all(
        cell in range(sudoku_logic.EMPTY, sudoku_logic.SIZE + 1)
        for row in puzzle
        for cell in row
    )
    assert all(
        cell in range(1, sudoku_logic.SIZE + 1)
        for row in solution
        for cell in row
    )