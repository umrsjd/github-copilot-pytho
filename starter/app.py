from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hint_count': 0,
    'hinted_cells': set(),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    try:
        if 'difficulty' in request.args:
            clues = sudoku_logic.clues_for_difficulty(
                request.args['difficulty']
            )
        else:
            clues = int(request.args.get('clues', 35))
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    except (TypeError, ValueError) as error:
        return jsonify({'error': str(error)}), 400
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hint_count'] = 0
    CURRENT['hinted_cells'] = set()
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request must be a JSON object'}), 400

    board = data.get('board')
    if (not isinstance(board, list)
            or len(board) != sudoku_logic.SIZE
            or any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE
                   for row in board)):
        return jsonify({'error': 'board must be a 9x9 array'}), 400

    if any(
        isinstance(cell, bool)
        or not isinstance(cell, int)
        or not sudoku_logic.EMPTY <= cell <= sudoku_logic.SIZE
        for row in board
        for cell in row
    ):
        return jsonify({'error': 'board cells must be integers between 0 and 9'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == sudoku_logic.EMPTY and board[i][j] != sudoku_logic.EMPTY:
                if board[i][j] != solution[i][j]:
                    incorrect.append([i, j])

    complete = all(
        puzzle[i][j] != sudoku_logic.EMPTY
        or board[i][j] == solution[i][j]
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
    )
    return jsonify({'incorrect': incorrect, 'complete': complete})

@app.route('/validate-move', methods=['POST'])
def validate_move():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request must be a JSON object'}), 400

    row = data.get('row')
    col = data.get('col')
    value = data.get('value')
    if not all(isinstance(item, int) and not isinstance(item, bool)
               for item in (row, col, value)):
        return jsonify({'error': 'row, col, and value must be integers'}), 400
    if not 0 <= row < sudoku_logic.SIZE or not 0 <= col < sudoku_logic.SIZE:
        return jsonify({'error': 'row and col must be between 0 and 8'}), 400
    if not 1 <= value <= sudoku_logic.SIZE:
        return jsonify({'error': 'value must be between 1 and 9'}), 400

    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if puzzle[row][col] != sudoku_logic.EMPTY:
        return jsonify({'error': 'Prefilled cells cannot be changed'}), 400

    return jsonify({'valid': value == solution[row][col]})

@app.route('/hint', methods=['POST'])
def request_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request must be a JSON object'}), 400

    row = data.get('row')
    col = data.get('col')
    if not all(isinstance(item, int) and not isinstance(item, bool)
               for item in (row, col)):
        return jsonify({'error': 'row and col must be integers'}), 400
    if not 0 <= row < sudoku_logic.SIZE or not 0 <= col < sudoku_logic.SIZE:
        return jsonify({'error': 'row and col must be between 0 and 8'}), 400

    eligible_cells = {
        (puzzle_row, puzzle_col)
        for puzzle_row in range(sudoku_logic.SIZE)
        for puzzle_col in range(sudoku_logic.SIZE)
        if puzzle[puzzle_row][puzzle_col] == sudoku_logic.EMPTY
    }
    if eligible_cells <= CURRENT['hinted_cells']:
        return jsonify({'error': 'No cells available for a hint'}), 400

    coordinate = (row, col)
    if puzzle[row][col] != sudoku_logic.EMPTY:
        return jsonify({'error': 'Prefilled cells cannot be changed'}), 400
    if coordinate in CURRENT['hinted_cells']:
        return jsonify({'error': 'This cell already has a hint'}), 400

    CURRENT['hinted_cells'].add(coordinate)
    CURRENT['hint_count'] += 1
    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col],
        'hint_count': CURRENT['hint_count'],
    })

if __name__ == '__main__':
    app.run(debug=True)