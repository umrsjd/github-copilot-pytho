import copy

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