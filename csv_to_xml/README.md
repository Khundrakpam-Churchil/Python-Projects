# CSV → XML / JSON Converter

A small Tkinter GUI tool to convert CSV files into well-formed XML or JSON while preserving the original data exactly.

## Features

- GUI application built with `tkinter` for easy file selection and conversion
- Robust CSV reading that tries multiple encodings and preserves all values as strings
- Outputs either pretty-printed UTF-8 XML or a UTF-8 JSON array of objects
- Post-write validation: re-reads output and compares row/column counts

## Requirements

- Python 3.10 or newer
- pandas (install with `pip install pandas`)
- `tkinter` (bundled with most Python installs; on some Linux distros install `python3-tk`)

## Installing

1. Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2.Install `pandas`:

```powershell
pip install pandas
```

## Usage

Run the application from the project folder:

```powershell
python convert.py
```

Steps in the GUI:

1. Click `Browse CSV` and select a CSV file (a `test-file.csv` is included for quick testing).
2. Choose the output format: `XML` or `JSON`.
3. Click `Convert`, choose a destination filename, and save.
4. The app will save the file and run a validation check comparing rows/columns to the original CSV.

## Notes

- The converter keeps every CSV cell as text (no automatic numeric coercion) and preserves empty cells as empty strings.
- Encodings attempted by the reader include: `utf-8-sig`, `utf-8`, `latin-1`, `cp1252`, `iso-8859-1`.
- XML element names are sanitised to be valid XML tags; duplicate CSV column names are handled safely.

## Files

- `convert.py` — main application source
- `test-file.csv` — small sample CSV for quick testing

## License

Unlicensed — feel free to use and adapt for personal or internal projects. Add a license file if you plan to redistribute.
