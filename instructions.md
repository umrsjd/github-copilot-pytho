# Sudoku Project Instructions

## Project Stack

- Python and Flask provide the application and server routes.
- Vanilla JavaScript provides browser interaction and state updates.
- HTML and CSS provide the semantic, responsive interface.
- pytest provides the Python test suite.

## Project Requirements

- The Sudoku board is 9x9, with valid rows, columns, and 3x3 regions.
- Every generated puzzle must have exactly one unique solution.
- Difficulty clue counts are Easy = 45, Medium = 35, and Hard = 30.
- Prefilled cells must be locked and hint-filled cells must also be locked.
- Invalid moves receive immediate visual and accessible feedback.
- Check Solution identifies incorrect entries and reports completion.
- Hint fills one correct value, locks it, and updates the hint count.
- Each game has a timer and a completion/congratulations message.
- Completed games are kept in a Top 10 leaderboard.
- The leaderboard uses browser localStorage key `sudokuLeaderboard` and
	persists across refreshes and browser reopening.
- A theme toggle supports light and dark themes using localStorage key
	`sudokuTheme`.
- 3x3 regions use alternating styling and clear region boundaries.
- The UI is responsive on desktop, tablet, and mobile layouts.
- Feedback and controls use accessible semantics and ARIA attributes.

## Coding Conventions

- Keep Flask responsibilities clear and keep Sudoku logic separate from
	presentation.
- Use meaningful names and keep functions focused.
- Handle errors meaningfully; do not silently swallow exceptions.
- Do not expose the Sudoku solution unnecessarily to the browser.
- Preserve existing API behavior unless a requirement explicitly requires a
	change.
- Avoid unnecessary dependencies and unrelated refactoring.

## Testing

- Use pytest for Python tests covering validation, solving, generation,
	difficulty counts, unique solutions, routes, and malformed input.
- Run the complete test suite after significant changes.
- Preserve existing behavior while refactoring.

## Copilot Guidance

- Inspect existing code and tests before modifying anything.
- Prefer small, focused changes that match the current architecture.
- Evaluate every suggestion against the explicit project requirements and
	existing behavior.
- Do not blindly accept suggestions; reject or adjust approaches that conflict
	with the requirements.
- Document significant Copilot-assisted decisions when they affect design.