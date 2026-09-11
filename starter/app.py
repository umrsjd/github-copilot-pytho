from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
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
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

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

if __name__ == '__main__':
    app.run(debug=True)