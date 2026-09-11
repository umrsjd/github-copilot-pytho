# Sudoku Game

## Overview

Sudoku Game is a Flask-based web application enhanced and refactored with GitHub Copilot. It generates playable Sudoku puzzles, provides immediate feedback while solving, and includes game progress, accessibility, theme, and leaderboard features in a browser-based interface.

## Features

- Generates valid 9x9 Sudoku puzzles from completed solution boards.
- Verifies that every generated puzzle has exactly one unique solution.
- Supports Easy, Medium, and Hard difficulty levels.
- Locks prefilled cells so they cannot be edited.
- Provides immediate invalid-move feedback for entered values.
- Includes a Check Solution action that identifies incorrect cells and detects completion.
- Provides hints that fill and lock a correct value and track the number of hints used.
- Runs a game timer for each new puzzle.
- Shows a completion summary and congratulations message when the puzzle is solved.
- Records a Top 10 leaderboard with player name, time, difficulty, and hints used.
- Persists leaderboard scores in browser `localStorage`.
- Supports Light and Dark mode.
- Persists the selected theme in browser `localStorage`.
- Uses responsive layouts for desktop, tablet, and mobile screen sizes.
- Uses alternating backgrounds for 3x3 Sudoku regions.
- Uses clear borders to mark 3x3 region boundaries.
- Provides accessible status announcements and invalid-cell feedback with ARIA attributes.

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- pytest
- GitHub Copilot

## Project Structure

```text
.
├── .github/
│   └── copilot-instructions.md
├── Screenshots/
├── starter/
│   ├── app.py
│   ├── requirements.txt
│   ├── sudoku_logic.py
│   ├── static/
│   ├── templates/
│   └── tests/
├── instruction.md
├── LICENSE.txt
├── CODEOWNERS
└── README.md
```

Important application files and directories:

- `starter/app.py` contains the Flask routes and in-memory current-game state.
- `starter/sudoku_logic.py` generates boards, removes clues, and validates unique solutions.
- `starter/templates/` contains the HTML page template.
- `starter/static/` contains the browser JavaScript and CSS.
- `starter/tests/` contains the pytest test suite for the Flask routes and Sudoku logic.
- `starter/requirements.txt` lists the Python dependencies.
- `Screenshots/` contains project screenshots.
- `instruction.md` contains the project instructions.
- `.github/copilot-instructions.md` contains repository-specific GitHub Copilot instructions.

## Installation

### Requirements

- Windows
- Python 3
- A modern web browser such as Microsoft Edge, Google Chrome, or Firefox

### Setup

In PowerShell or Command Prompt, clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd github-copilot-python
```

Create and activate a virtual environment from the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the dependencies and enter the Flask application directory:

```bash
cd starter
python -m pip install -r requirements.txt
```

## Running the Application

From the `starter` directory, start the Flask development server:

```bash
python app.py
```

Open the following address in a web browser:

http://127.0.0.1:5000

## Running Tests

From the `starter` directory, run the complete test suite:

```bash
python -m pytest
```

The tests cover puzzle generation, clue counts, unique-solution behavior, Sudoku solving and validation logic, Flask endpoints, malformed requests, move validation, hints, and completion checks.

## How the Game Works

1. Choose Easy, Medium, or Hard and start a new game.
2. Enter values in the empty cells. Values are checked immediately by the Flask backend.
3. Use Check Solution to review the current board or Hint to fill one correct empty cell.
4. Complete the puzzle to stop the timer and display the completion summary.
5. Enter a name when prompted to add the result to the browser’s Top 10 leaderboard.

Leaderboard scores and the selected theme are stored locally in the browser and are not sent to a server for permanent storage.

## Difficulty Levels

| Difficulty | Clues |
|---|---:|
| Easy | 45 |
| Medium | 35 |
| Hard | 30 |

The generator creates a completed valid board, removes clues for the selected difficulty, and verifies that the resulting puzzle has exactly one unique solution.

## Leaderboard

The leaderboard keeps the Top 10 fastest completed games. Each entry records:

- Player name
- Completion time
- Difficulty
- Hints used

Scores are sorted fastest-first and stored in browser `localStorage` under the key `sudokuLeaderboard`. They remain available after a page refresh or browser reopening. Starting a New Game or changing the difficulty does not clear existing scores.

Malformed, invalid, or unavailable `localStorage` data is handled safely by falling back to an empty or valid filtered leaderboard. There is no server-side leaderboard database; scores are stored only in the current browser.

## Dark Mode

The Light/Dark toggle changes the theme of the entire user interface, including the page, board, controls, status messages, completion summary, and leaderboard. The selected theme is persisted in browser `localStorage` under the key `sudokuTheme`. Invalid stored theme values safely fall back to Light mode.

## Responsive Design

The interface supports desktop, tablet, and mobile layouts. The Sudoku grid keeps its 9x9 structure and scales its cells for smaller screens. The leaderboard remains usable on narrow screens through contained horizontal overflow rather than expanding beyond the page.

## GitHub Copilot Usage

GitHub Copilot was used throughout the project for understanding the legacy code, planning changes, implementation, test creation, debugging, and QA/review. Suggestions were reviewed and evaluated against the application requirements and test results rather than blindly accepted.

## Testing and QA

Validation performed for the completed project includes:

- 73 passing pytest tests covering Sudoku logic and Flask routes.
- JavaScript syntax validation.
- `git diff --check`.
- Manual browser testing of difficulty selection, invalid-move feedback, hints, timer and completion behavior, leaderboard behavior, Light/Dark mode, responsive/mobile layouts, and 3x3 region styling.

## Screenshots

The `Screenshots/` directory contains evidence of the development process and completed features, including GitHub Copilot planning and implementation screenshots and browser verification screenshots.

Examples include:

- Copilot planning and implementation: `copilot_difficulty_plan.png`, `copilot_completion_implementation.png`, `copilot_testing_plan1.png`, `copilot_async_fix_implementation.png`
- Browser verification: `difficulty` evidence in `copilot_difficulty_plan5.png`, `invalid_move_feedback.png`, `hint_success.png`, `timer_running.png`, `leaderboard_success.png`, `responsive_mobile.png`, `grid_3x3_dark_mode.png`, `grid_3x3_styling.png`
- Theme and completion evidence: `copilot_dark_mode_implementation.png`, `copilot_completion_implementation.png`

## Known Limitation

The Flask application's current puzzle, solution, and hint state is stored in process memory. It is intended for a local or single-user demonstration environment rather than production multi-user deployment.

## GitHub Copilot Instructions

`instruction.md` contains the project-level development instructions. `.github/copilot-instructions.md` contains repository-specific instructions for GitHub Copilot, including the project requirements, coding principles, Sudoku rules, Flask responsibilities, frontend expectations, testing guidance, and Git conventions.

## License

This project includes the license terms in [LICENSE.txt](LICENSE.txt).
