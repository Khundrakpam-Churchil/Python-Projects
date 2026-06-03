# Simple Quiz

A small command-line quiz script implemented in `Simple_Quiz.py`.

## Summary

`Simple_Quiz.py` provides a simple multiple-question quiz and integrates with the `Number_guesing` game to present a small games menu and show the last results.

## Requirements

- Python 3 (3.8+ recommended)

No external packages required — uses only the Python standard library and the sibling module `Number_guesing`.

## Running

From the `Use Loop` folder run:

```powershell
python Simple_Quiz.py
```

Or provide the full path:

```powershell
python "d:\Python-Projects\Use Loop\Simple_Quiz.py"
```

## Menu options

- `1` — Play Simple Quiz: prompts three questions and scores your answers.
- `2` — Play Number Guessing Game: launches `Number_guesing.py`.
- `3` — Show Last Results: displays the most recent quiz score and the last completed number guessing game results (if any).
- `4` — Exit the menu.

## How the quiz works

- The quiz questions are stored in the `quiz_data` list as `(question, answer)` tuples near the top of the script.
- Answers are compared case-insensitively after trimming whitespace.
- After each question you are told whether your answer was correct; at the end you receive a summary score.

## Modifying the quiz

- To add or change questions, edit the `quiz_data` variable in `Simple_Quiz.py`. Each entry should be a tuple of the prompt and the expected answer string.

## Notes

- The script uses `Number_guesing` module variables (e.g., `last_result`, `last_number`, `last_attempts`, `last_hint`) to show cross-game results; run the number guessing game first to populate those values.
- Input validation is minimal — enter integers for menu choices and free-text answers for quiz prompts.

## Possible improvements

- Add persistence for player stats (best score, history).
- Support multiple-choice questions and timed quizzes.
- Add command-line flags to run a single mode directly (quiz or guessing game).
