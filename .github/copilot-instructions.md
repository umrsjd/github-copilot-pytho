# Sudoku Project Development Instructions

## Project Overview

This project is a Flask-based Sudoku game being refactored from legacy
Python code into a clean, maintainable application.

The final application must support:

- Easy, Medium, and Hard difficulty levels
- Sudoku puzzles with exactly one unique solution
- Locked prefilled cells
- Immediate invalid move feedback
- Puzzle completion detection
- Hint functionality
- Check functionality
- Game timer
- Top 10 leaderboard
- LocalStorage persistence
- Dark/light mode
- Responsive desktop and mobile layouts
- Accessible and readable controls

## Development Principles

Write clean, readable, maintainable Python, JavaScript, HTML, and CSS.

Prefer small, focused functions instead of large functions.

Avoid unnecessary code duplication.

Use descriptive variable and function names.

Add comments where the logic is non-obvious, especially around Sudoku
generation, solving, and unique-solution validation.

Do not introduce unnecessary dependencies.

Preserve existing functionality when refactoring unless a requirement
explicitly calls for changing it.

## Sudoku Logic

Sudoku boards must contain numbers from 1 through 9.

Rows, columns, and 3x3 boxes must contain no duplicate numbers.

Generated puzzles must have exactly one valid solution.

When removing numbers from a solved board, verify that the resulting
puzzle still has exactly one solution.

Difficulty levels should control the number of prefilled cells.

Prefilled and hint-generated cells must be locked.

## Flask

Keep backend responsibilities separate from frontend responsibilities.

Use Flask routes for game-related server functionality.

Validate user-controlled input.

Return clear error responses when appropriate.

## Frontend

Use semantic HTML.

Keep JavaScript modular and readable.

Use CSS media queries for responsive layouts.

The Sudoku grid must maintain its structure on small screens.

The 3x3 Sudoku regions should have alternating visual styling.

The application must support both light and dark themes.

Buttons and text must remain readable in both themes.

## Testing

Use pytest for Python tests.

Tests should cover Sudoku validation, solving, puzzle generation,
and unique-solution behavior.

Run the complete test suite after significant changes.

Do not consider a feature complete until the relevant tests pass.

## Git

Make focused commits.

Use descriptive commit messages.

Do not commit:

- .venv
- __pycache__
- *.pyc
- secrets
- API keys
- unnecessary generated files

## GitHub Copilot

Use Copilot as an assistant rather than blindly accepting generated code.

Review suggestions before accepting them.

If a suggestion is incorrect, reject or modify it.

Document significant Copilot-assisted decisions where useful.