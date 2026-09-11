import copy

import pytest

import app as app_module
import sudoku_logic


def test_get_root_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_get_new_returns_puzzle_and_stores_solution(client):
    response = client.get('/new')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert app_module.CURRENT['puzzle'] == puzzle
    assert app_module.CURRENT['solution'] is not None


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 45), ('medium', 35), ('hard', 30)],
)
def test_get_new_supports_difficulty_levels(client, difficulty, expected_clues):
    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == expected_clues


def test_get_new_rejects_invalid_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'difficulty must be easy, medium, or hard'
    }


def test_get_new_preserves_legacy_clues_parameter(client):
    response = client.get('/new?clues=40')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40


def test_post_check_before_new_game_returns_error(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_post_check_with_correct_solution_returns_no_incorrect_cells(client):
    client.get('/new')
    solution = copy.deepcopy(app_module.CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'complete': True}


def test_post_check_reports_incorrect_solution_cell(client):
    client.get('/new')
    puzzle = app_module.CURRENT['puzzle']
    solution = app_module.CURRENT['solution']
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] == sudoku_logic.EMPTY
    )
    board = copy.deepcopy(solution)
    board[row][col] = solution[row][col] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {
        'incorrect': [[row, col]],
        'complete': False,
    }


def test_post_check_does_not_report_blank_cells_and_is_incomplete(client):
    client.get('/new')

    response = client.post('/check', json={
        'board': sudoku_logic.create_empty_board(),
    })

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'complete': False}


def test_post_check_ignores_prefilled_cells(client):
    client.get('/new')
    puzzle = app_module.CURRENT['puzzle']
    board = copy.deepcopy(app_module.CURRENT['solution'])
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != sudoku_logic.EMPTY
    )
    board[row][col] = board[row][col] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'complete': True}


@pytest.mark.parametrize(
    'payload',
    [
        {},
        {'board': []},
        {'board': [[0] * sudoku_logic.SIZE for _ in range(8)]},
        {'board': [[0] * 8 for _ in range(sudoku_logic.SIZE)]},
        {'board': [[None] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]},
        {'board': [[True] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]},
        {'board': [[1.5] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]},
        {'board': [[-1] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]},
        {'board': [[10] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]},
    ],
)
def test_post_check_rejects_malformed_board_payloads(client, payload):
    client.get('/new')

    response = client.post('/check', json=payload)

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_post_check_rejects_non_json_request(client):
    client.get('/new')

    response = client.post('/check', data='not json')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request must be a JSON object'}


def test_post_check_response_does_not_expose_solution(client):
    client.get('/new')
    solution = copy.deepcopy(app_module.CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'complete': True}
    assert 'solution' not in response.get_json()


def test_validate_move_before_new_game_returns_error(client):
    response = client.post('/validate-move', json={
        'row': 0,
        'col': 0,
        'value': 1,
    })

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_validate_move_compares_candidate_with_solution(client):
    client.get('/new')
    puzzle = app_module.CURRENT['puzzle']
    solution = app_module.CURRENT['solution']
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] == sudoku_logic.EMPTY
    )

    valid_response = client.post('/validate-move', json={
        'row': row,
        'col': col,
        'value': solution[row][col],
    })
    invalid_response = client.post('/validate-move', json={
        'row': row,
        'col': col,
        'value': solution[row][col] % sudoku_logic.SIZE + 1,
    })

    assert valid_response.status_code == 200
    assert valid_response.get_json() == {'valid': True}
    assert invalid_response.status_code == 200
    assert invalid_response.get_json() == {'valid': False}


def test_validate_move_rejects_prefilled_cell(client):
    client.get('/new')
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if app_module.CURRENT['puzzle'][row][col] != sudoku_logic.EMPTY
    )

    response = client.post('/validate-move', json={
        'row': row,
        'col': col,
        'value': app_module.CURRENT['solution'][row][col],
    })

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Prefilled cells cannot be changed'}


@pytest.mark.parametrize(
    ('payload', 'error'),
    [
        ({'row': -1, 'col': 0, 'value': 1}, 'row and col must be between 0 and 8'),
        ({'row': 0, 'col': 9, 'value': 1}, 'row and col must be between 0 and 8'),
        ({'row': 0, 'col': 0, 'value': 0}, 'value must be between 1 and 9'),
        ({'row': 0, 'col': 0, 'value': 10}, 'value must be between 1 and 9'),
        ({'row': '0', 'col': 0, 'value': 1}, 'row, col, and value must be integers'),
    ],
)
def test_validate_move_rejects_invalid_payload(client, payload, error):
    client.get('/new')

    response = client.post('/validate-move', json=payload)

    assert response.status_code == 400
    assert response.get_json() == {'error': error}


def test_validate_move_handles_non_json_request(client):
    client.get('/new')

    response = client.post('/validate-move', data='not json')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request must be a JSON object'}


def first_empty_cell():
    return next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if app_module.CURRENT['puzzle'][row][col] == sudoku_logic.EMPTY
    )


def first_prefilled_cell():
    return next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if app_module.CURRENT['puzzle'][row][col] != sudoku_logic.EMPTY
    )


def test_post_hint_returns_one_correct_value_and_increments_count(client):
    client.get('/new')
    row, col = first_empty_cell()

    response = client.post('/hint', json={'row': row, 'col': col})

    assert response.status_code == 200
    assert response.get_json() == {
        'row': row,
        'col': col,
        'value': app_module.CURRENT['solution'][row][col],
        'hint_count': 1,
    }
    assert app_module.CURRENT['hint_count'] == 1
    assert (row, col) in app_module.CURRENT['hinted_cells']
    assert 'solution' not in response.get_json()


def test_post_hint_increments_count_for_each_successful_hint(client):
    client.get('/new')
    first = first_empty_cell()
    second = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if app_module.CURRENT['puzzle'][row][col] == sudoku_logic.EMPTY
        and (row, col) != first
    )

    first_response = client.post('/hint', json={'row': first[0], 'col': first[1]})
    second_response = client.post('/hint', json={'row': second[0], 'col': second[1]})

    assert first_response.get_json()['hint_count'] == 1
    assert second_response.get_json()['hint_count'] == 2
    assert app_module.CURRENT['hint_count'] == 2


def test_post_hint_rejects_prefilled_cell(client):
    client.get('/new')
    row, col = first_prefilled_cell()

    response = client.post('/hint', json={'row': row, 'col': col})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Prefilled cells cannot be changed'}
    assert app_module.CURRENT['hint_count'] == 0


def test_post_hint_rejects_already_hinted_cell(client):
    client.get('/new')
    row, col = first_empty_cell()
    client.post('/hint', json={'row': row, 'col': col})

    response = client.post('/hint', json={'row': row, 'col': col})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'This cell already has a hint'}
    assert app_module.CURRENT['hint_count'] == 1


def test_post_hint_returns_no_available_cells_after_all_empty_cells_are_hinted(client):
    client.get('/new')
    empty_cells = [
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if app_module.CURRENT['puzzle'][row][col] == sudoku_logic.EMPTY
    ]

    for row, col in empty_cells:
        response = client.post('/hint', json={'row': row, 'col': col})
        assert response.status_code == 200

    response = client.post('/hint', json={'row': empty_cells[0][0], 'col': empty_cells[0][1]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No cells available for a hint'}
    assert app_module.CURRENT['hint_count'] == len(empty_cells)


def test_post_hint_before_new_game_returns_error(client):
    response = client.post('/hint', json={'row': 0, 'col': 0})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize(
    'payload',
    [
        {},
        {'row': 0},
        {'col': 0},
        {'row': '0', 'col': 0},
        {'row': 0, 'col': '0'},
        {'row': True, 'col': 0},
        {'row': 0, 'col': False},
    ],
)
def test_post_hint_rejects_malformed_payload(client, payload):
    client.get('/new')

    response = client.post('/hint', json=payload)

    assert response.status_code == 400
    assert response.get_json() == {'error': 'row and col must be integers'}


def test_post_hint_rejects_non_json_request(client):
    client.get('/new')

    response = client.post('/hint', data='not json')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request must be a JSON object'}


@pytest.mark.parametrize(
    ('row', 'col'),
    [(-1, 0), (0, -1), (9, 0), (0, 9)],
)
def test_post_hint_rejects_invalid_coordinates(client, row, col):
    client.get('/new')

    response = client.post('/hint', json={'row': row, 'col': col})

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'row and col must be between 0 and 8'
    }


def test_new_game_resets_hint_state(client):
    client.get('/new?difficulty=hard')
    row, col = first_empty_cell()
    client.post('/hint', json={'row': row, 'col': col})

    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    assert app_module.CURRENT['hint_count'] == 0
    assert app_module.CURRENT['hinted_cells'] == set()