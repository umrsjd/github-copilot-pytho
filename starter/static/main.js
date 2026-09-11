// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let validationVersions = [];

function cellIndex(row, col) {
  return row * SIZE + col;
}

function setCellState(input, state) {
  input.className = 'sudoku-cell';
  input.dataset.state = state;
  input.setAttribute('aria-invalid', state === 'incorrect' ? 'true' : 'false');

  if (state === 'prefilled') {
    input.classList.add('prefilled');
    input.disabled = true;
    input.setAttribute('aria-label', `Row ${Number(input.dataset.row) + 1}, column ${Number(input.dataset.col) + 1}, prefilled`);
    input.removeAttribute('aria-describedby');
  } else if (state === 'user-entered') {
    input.classList.add('user-entered');
    input.disabled = false;
    input.setAttribute('aria-label', `Row ${Number(input.dataset.row) + 1}, column ${Number(input.dataset.col) + 1}, user entered`);
    input.removeAttribute('aria-describedby');
  } else if (state === 'incorrect') {
    input.classList.add('user-entered', 'incorrect');
    input.disabled = false;
    input.setAttribute('aria-label', `Row ${Number(input.dataset.row) + 1}, column ${Number(input.dataset.col) + 1}, incorrect value`);
    input.setAttribute('aria-describedby', 'message');
  } else {
    input.disabled = false;
    input.setAttribute('aria-label', `Row ${Number(input.dataset.row) + 1}, column ${Number(input.dataset.col) + 1}, empty`);
    input.removeAttribute('aria-describedby');
  }
}

function setMessage(text, isError = false) {
  const message = document.getElementById('message');
  message.innerText = text;
  message.style.color = isError ? '#d32f2f' : '';
}

async function validateCell(input, value, version) {
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const response = await fetch('/validate-move', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({row, col, value: Number(value)})
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Unable to validate move.');
  }
  if (validationVersions[cellIndex(row, col)] !== version || input.value !== value) {
    return;
  }

  if (data.valid) {
    setCellState(input, 'user-entered');
    setMessage('');
  } else {
    setCellState(input, 'incorrect');
    setMessage(`Incorrect value in row ${row + 1}, column ${col + 1}.`, true);
  }
}

function handleCellInput(event) {
  const input = event.target;
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const index = cellIndex(row, col);
  const version = validationVersions[index] + 1;
  validationVersions[index] = version;
  const value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
  input.value = value;

  if (!value) {
    setCellState(input, 'empty');
    setMessage('');
    return;
  }

  setCellState(input, 'user-entered');
  validateCell(input, value, version).catch((error) => {
    if (validationVersions[index] !== version || input.value !== value) {
      return;
    }
    setCellState(input, 'user-entered');
    setMessage(error.message, true);
  });
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  validationVersions = Array(SIZE * SIZE).fill(0);
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', handleCellInput);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        setCellState(inp, 'prefilled');
      } else {
        inp.value = '';
        setCellState(inp, 'empty');
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error || 'Unable to start a new game.';
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error || 'Unable to check solution.';
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    if (incorrect.has(idx)) {
      setCellState(inp, 'incorrect');
    } else if (inp.value) {
      setCellState(inp, 'user-entered');
    } else {
      setCellState(inp, 'empty');
    }
  }
  if (data.complete) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else if (incorrect.size > 0) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  } else {
    msg.style.color = '';
    msg.innerText = 'Keep filling in the puzzle.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  // initialize
  newGame();
});