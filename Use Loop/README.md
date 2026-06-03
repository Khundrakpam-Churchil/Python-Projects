# Number Guessing Game

A small command-line number guessing game implemented in `Number_guesing.py`.

## Summary

The program chooses a random integer between 1 and 100 and asks the player to guess it. Feedback is given after each guess; helpful hints appear after several incorrect attempts.

## Requirements

- Python 3 (3.8+ recommended)

No external packages are required — the game uses only the Python standard library.

## Running

From the `Use Loop` folder run:

```powershell
python Number_guesing.py
```

Or provide the full path to the script from anywhere:

```powershell
python "d:\Python-Projects\Use Loop\Number_guesing.py"
```

## How to play

- The program picks a number between 1 and 100.
- Enter integer guesses when prompted.
- After each guess you'll be told whether your guess is too low or too high.
- After 3 incorrect attempts you'll receive a hint whether the secret number is EVEN or ODD.
- After 6 incorrect attempts you'll receive a divisor hint (a number between 2 and 10 that evenly divides the secret number) if one exists; otherwise you'll be told the number appears to be prime (or has no small divisors under 11).

## Notes

- Non-integer input will prompt you to enter a valid integer.
- The script records the number of attempts and prints a congratulatory message when you guess correctly.

## File

- `Number_guesing.py` — main script

## Possible improvements

- Add command-line options (range, verbose mode).
- Persist player statistics (best score, average attempts).
- Add difficulty levels (smaller/larger ranges).
