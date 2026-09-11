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
    assert response.get_json() == {'incorrect': []}


def test_post_check_reports_incorrect_solution_cell(client):
    client.get('/new')
    board = copy.deepcopy(app_module.CURRENT['solution'])
    board[0][0] = board[0][0] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


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