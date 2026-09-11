// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let validationVersions = [];
let hintCount = 0;
let hintedCells = new Set();
let timerInterval = null;
let timerStartTime = null;
let elapsedSeconds = 0;
let newGameRequestVersion = 0;
let gameCompleted = false;
let finalElapsedSeconds = null;

function formatElapsedTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function renderTimer() {
  document.getElementById('game-timer').innerText = formatElapsedTime(elapsedSeconds);
}

function updateElapsedTime() {
  elapsedSeconds = Math.floor((Date.now() - timerStartTime) / 1000);
  renderTimer();
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  if (timerStartTime !== null) {
    updateElapsedTime();
    timerStartTime = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  renderTimer();
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  timerStartTime = Date.now();
  renderTimer();
  timerInterval = setInterval(updateElapsedTime, 1000);
}

function getElapsedSeconds() {
  return elapsedSeconds;
}

window.getElapsedSeconds = getElapsedSeconds;

function setCompletionSummary(time, difficulty, hints) {
  document.getElementById('completion-time').innerText = time;
  document.getElementById('completion-difficulty').innerText = difficulty;
  document.getElementById('completion-hints').innerText = String(hints);
  document.getElementById('completion-summary').hidden = false;
}

function resetCompletionState() {
  gameCompleted = false;
  finalElapsedSeconds = null;
  document.getElementById('completion-summary').hidden = true;
  document.getElementById('check-solution').disabled = false;
  document.getElementById('hint').disabled = false;
}

function completeGame() {
  stopTimer();
  gameCompleted = true;
  finalElapsedSeconds = getElapsedSeconds();

  const difficulty = document.getElementById('difficulty');
  const selectedDifficulty = difficulty.options[difficulty.selectedIndex].text;
  setCompletionSummary(
    formatElapsedTime(finalElapsedSeconds),
    selectedDifficulty,
    hintCount
  );

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  for (const input of inputs) {
    input.disabled = true;
  }
  document.getElementById('check-solution').disabled = true;
  document.getElementById('hint').disabled = true;
  setMessage('Congratulations! You solved it.');
}

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
  } else if (state === 'hint') {
    input.classList.add('hint');
    input.disabled = true;
    input.setAttribute('aria-label', `Row ${Number(input.dataset.row) + 1}, column ${Number(input.dataset.col) + 1}, hint`);
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

function setHintCount(count) {
  hintCount = count;
  document.getElementById('hint-count').innerText = `Hints used: ${hintCount}`;
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
  if (gameCompleted) {
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
  if (gameCompleted) {
    return;
  }
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
  hintedCells = new Set();
  setHintCount(0);
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
  const requestVersion = ++newGameRequestVersion;
  resetCompletionState();
  resetTimer();
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (requestVersion !== newGameRequestVersion) {
    return;
  }
  if (!res.ok) {
    setMessage(data.error || 'Unable to start a new game.', true);
    return;
  }
  renderPuzzle(data.puzzle);
  setMessage('');
  startTimer();
}

async function checkSolution() {
  if (gameCompleted) {
    return;
  }
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
  if (gameCompleted) {
    return;
  }
  if (!res.ok) {
    setMessage(data.error || 'Unable to check solution.', true);
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
    completeGame();
  } else if (incorrect.size > 0) {
    setMessage('Some cells are incorrect.', true);
  } else {
    setMessage('Keep filling in the puzzle.');
  }
}

function findHintTarget() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  for (const input of inputs) {
    if (!input.disabled && input.dataset.state === 'incorrect') {
      return input;
    }
  }
  for (const input of inputs) {
    if (!input.disabled && !input.value) {
      return input;
    }
  }
  return null;
}

async function requestHint() {
  if (gameCompleted) {
    return;
  }
  const target = findHintTarget();
  if (!target) {
    setMessage('No cells are available for a hint.', true);
    return;
  }

  const row = Number(target.dataset.row);
  const col = Number(target.dataset.col);
  const index = cellIndex(row, col);
  validationVersions[index] += 1;

  const response = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({row, col})
  });
  const data = await response.json();
  if (!response.ok) {
    setMessage(data.error || 'Unable to provide a hint.', true);
    return;
  }

  const hintedInput = document.getElementById('sudoku-board').getElementsByTagName('input')[cellIndex(data.row, data.col)];
  hintedInput.value = data.value;
  hintedCells.add(cellIndex(data.row, data.col));
  setCellState(hintedInput, 'hint');
  setHintCount(data.hint_count);
  if (findHintTarget()) {
    setMessage('A correct value was filled in and locked as a hint.');
  } else {
    await checkSolution();
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  // initialize
  newGame();
});