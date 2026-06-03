"""
CSV to XML / JSON Converter
============================
A Tkinter GUI application that converts CSV files into XML or JSON
while preserving 100% of the original data.

Requirements: Python 3.10+, pandas, tkinter (stdlib)
Install deps : pip install pandas
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard-library imports
# ─────────────────────────────────────────────────────────────────────────────
import json
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom

# ─────────────────────────────────────────────────────────────────────────────
# Third-party imports
# ─────────────────────────────────────────────────────────────────────────────
try:
    import pandas as pd
except ImportError:
    print("pandas is required. Install it with:  pip install pandas")
    sys.exit(1)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 – CSV Reading helpers
# ═════════════════════════════════════════════════════════════════════════════

COMMON_ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252", "iso-8859-1"]


def detect_and_read_csv(filepath: str) -> pd.DataFrame:
    """
    Try each encoding in COMMON_ENCODINGS until the file loads without errors.
    Returns a DataFrame with all values kept as strings (dtype=str) so that
    numeric columns are not silently reformatted and NaN is never injected.
    """
    last_error = None
    for enc in COMMON_ENCODINGS:
        try:
            df = pd.read_csv(
                filepath,
                encoding=enc,
                dtype=str,          # keep everything as text – no type coercion
                keep_default_na=False,  # empty cells stay "", not NaN
                na_values=[],       # disable all automatic NA recognition
                skipinitialspace=False,
            )
            return df
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_error = exc
            continue
        except Exception as exc:           # noqa: BLE001
            raise RuntimeError(f"Could not parse CSV: {exc}") from exc

    raise RuntimeError(
        f"Unable to decode '{filepath}' with any of {COMMON_ENCODINGS}.\n"
        f"Last error: {last_error}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 – XML conversion helpers
# ═════════════════════════════════════════════════════════════════════════════

# Characters that are allowed as the *start* of an XML tag name
_XML_NAME_START = re.compile(r"[^a-zA-Z_\u00C0-\u00D6\u00D8-\u00F6"
                              r"\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF"
                              r"\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF"
                              r"\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD]")

# Characters allowed *anywhere else* in an XML tag name (adds digits, -, .)
_XML_NAME_CONT = re.compile(r"[^a-zA-Z0-9_.\-\u00B7\u00C0-\u00D6\u00D8-\u00F6"
                             r"\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF"
                             r"\u200C-\u200D\u203F-\u2040\u2070-\u218F"
                             r"\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF"
                             r"\uFDF0-\uFFFD]")


def sanitize_xml_tag(name: str) -> str:
    """
    Convert an arbitrary string into a valid XML element name.

    Steps
    -----
    1. Replace spaces and common punctuation with underscores.
    2. If the first character is a digit, prepend 'col_' so the digit
       becomes a valid *continuation* character.
    3. Sanitise the first character using the XML NameStartChar rule.
    4. Sanitise remaining characters using the XML NameChar rule.
    5. Avoid the reserved 'xml' prefix (case-insensitive).
    """
    if not name:
        return "col_empty"

    # Replace spaces and common separators / symbols with underscores
    tag = re.sub(r"[\s/\\()\[\]{}<>?!@#$%^&*+=|;:'\"`,~]", "_", name)

    if not tag:
        return "col_"

    # If the first character is a digit, prepend 'col_' so all original
    # characters become continuation characters (digits are legal there).
    if tag[0].isdigit():
        tag = "col_" + tag

    # Sanitise first character against NameStartChar rules
    first = _XML_NAME_START.sub("_", tag[0])
    # Sanitise the rest against NameChar rules
    rest  = _XML_NAME_CONT.sub("_", tag[1:]) if len(tag) > 1 else ""
    tag = first + rest

    # Final safety: must not be empty
    if not tag:
        tag = "col_"

    # Avoid the reserved 'xml' prefix (case-insensitive)
    if tag.lower().startswith("xml"):
        tag = "x_" + tag

    return tag


def build_tag_map(columns: list[str]) -> list[str]:
    """
    Return a list of unique XML tag names, one per column, in column order.

    Uses a positional list rather than a dict so that DataFrames with
    duplicate column names are handled correctly (duplicate keys would
    silently overwrite each other in a dict).

    Uniqueness is guaranteed by appending _2, _3 … on collision.
    """
    tags: list[str] = []
    seen: dict[str, int] = {}

    for col in columns:
        tag = sanitize_xml_tag(col)
        if tag in seen:
            seen[tag] += 1
            unique_tag = f"{tag}_{seen[tag]}"
        else:
            seen[tag] = 1
            unique_tag = tag
        tags.append(unique_tag)

    return tags


def dataframe_to_xml(df: pd.DataFrame) -> bytes:
    """
    Convert a pandas DataFrame to a well-formed UTF-8 XML document.

    Structure:
        <records>
            <record>
                <ColumnName>value</ColumnName>
                …
            </record>
            …
        </records>

    Returns the XML as UTF-8 encoded bytes.
    """
    tags = build_tag_map(list(df.columns))

    root = Element("records")

    for _, row in df.iterrows():
        record_el = SubElement(root, "record")
        for idx, tag in enumerate(tags):
            child = SubElement(record_el, tag)
            # Use iloc so duplicate column names are handled safely
            val = row.iloc[idx]
            child.text = val if val != "" else None

    # Pretty-print via minidom
    raw_xml = tostring(root, encoding="unicode")
    dom = minidom.parseString(raw_xml)
    pretty = dom.toprettyxml(indent="  ", encoding="utf-8")

    # minidom adds a second declaration – keep only the first line
    lines = pretty.decode("utf-8").splitlines()
    # Ensure there is exactly one XML declaration at the top
    declaration = '<?xml version="1.0" encoding="utf-8"?>'
    body_lines = [ln for ln in lines if not ln.strip().startswith("<?xml")]
    result = declaration + "\n" + "\n".join(body_lines)

    return result.encode("utf-8")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 – JSON conversion helpers
# ═════════════════════════════════════════════════════════════════════════════

def dataframe_to_json_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert a pandas DataFrame to a UTF-8 JSON array of objects.
    Column names are used as-is.  Empty cells become "" (not null / "nan").
    """
    records = []
    for _, row in df.iterrows():
        obj = {col: row[col] for col in df.columns}
        records.append(obj)

    json_str = json.dumps(records, ensure_ascii=False, indent=2)
    return json_str.encode("utf-8")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 – Validation helpers
# ═════════════════════════════════════════════════════════════════════════════

def validate_output(
    original_df: pd.DataFrame,
    output_path: str,
    fmt: str,
) -> tuple[bool, str]:
    """
    Re-read the output file and verify row/column counts against the source.
    Returns (passed: bool, message: str).
    """
    orig_rows, orig_cols = original_df.shape

    try:
        if fmt == "json":
            with open(output_path, encoding="utf-8") as fh:
                data = json.load(fh)
            out_rows = len(data)
            out_cols = len(data[0]) if data else 0

        else:  # xml
            import xml.etree.ElementTree as ET  # noqa: PLC0415
            tree = ET.parse(output_path)
            root = tree.getroot()
            records = list(root)
            out_rows = len(records)
            out_cols = max((len(list(r)) for r in records), default=0)

    except Exception as exc:  # noqa: BLE001
        return False, f"Validation error while re-reading output: {exc}"

    issues = []
    if out_rows != orig_rows:
        issues.append(f"Row count mismatch – expected {orig_rows}, got {out_rows}")
    if out_cols != orig_cols:
        issues.append(f"Column count mismatch – expected {orig_cols}, got {out_cols}")

    if issues:
        return False, "  •  " + "\n  •  ".join(issues)

    return True, (
        f"Validation passed ✓\n"
        f"  Rows : {out_rows} / {orig_rows}\n"
        f"  Cols : {out_cols} / {orig_cols}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 – GUI Application
# ═════════════════════════════════════════════════════════════════════════════

# ── Colour palette ────────────────────────────────────────────────────────────
BG          = "#1E1E2E"   # main background (dark)
BG_CARD     = "#2A2A3E"   # card / panel background
BG_ENTRY    = "#313145"   # input field background
ACCENT      = "#7C6AF7"   # primary accent (violet)
ACCENT_DARK = "#5A4BD1"   # pressed / hover accent
SUCCESS     = "#50FA7B"   # green for success
WARNING     = "#FFB86C"   # amber for warning
ERROR       = "#FF5555"   # red for error
FG          = "#CDD6F4"   # primary text
FG_DIM      = "#6C7086"   # muted text
BTN_EXIT_BG = "#45475A"   # exit button background

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_LABEL_B= ("Segoe UI", 10, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")


class CSVConverterApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("CSV → XML / JSON Converter")
        self.resizable(True, True)
        self.minsize(700, 560)
        self.configure(bg=BG)

        # ── State variables ──────────────────────────────────────────────────
        self.csv_path    = tk.StringVar()
        self.format_var  = tk.StringVar(value="xml")   # "xml" or "json"
        self.status_var  = tk.StringVar(value="Ready – select a CSV file to begin.")
        self.df: pd.DataFrame | None = None             # loaded DataFrame

        self._build_ui()
        self._centre_window()

    # ──────────────────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construct every widget in the window."""

        # ── Title bar ─────────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=ACCENT, padx=20, pady=14)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="⟳  CSV Converter",
            font=FONT_TITLE,
            bg=ACCENT,
            fg="#FFFFFF",
        ).pack(side="left")

        tk.Label(
            title_frame,
            text="XML  &  JSON",
            font=("Segoe UI", 11),
            bg=ACCENT,
            fg="#E0DAFF",
        ).pack(side="right", padx=4)

        # ── Main content ──────────────────────────────────────────────────────
        content = tk.Frame(self, bg=BG, padx=20, pady=16)
        content.pack(fill="both", expand=True)

        # ── File-selection card ───────────────────────────────────────────────
        self._card(content, "📂  Source CSV File", self._build_file_section)

        # ── Format selection + info card ──────────────────────────────────────
        self._card(content, "🔄  Output Format", self._build_format_section)

        # ── Action buttons ────────────────────────────────────────────────────
        self._build_action_buttons(content)

        # ── Log / status panel ────────────────────────────────────────────────
        self._card(content, "📋  Log", self._build_log_section)

        # ── Bottom status bar ─────────────────────────────────────────────────
        status_bar = tk.Frame(self, bg=BG_CARD, pady=6)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=FG_DIM,
            anchor="w",
            padx=16,
        ).pack(fill="x")

    def _card(self, parent, title: str, builder_fn):
        """Create a titled card container and call builder_fn inside it."""
        outer = tk.Frame(parent, bg=BG_CARD, pady=0)
        outer.pack(fill="x", pady=(0, 12))

        # header strip
        hdr = tk.Frame(outer, bg=ACCENT_DARK, padx=12, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=FONT_LABEL_B, bg=ACCENT_DARK, fg="#FFFFFF").pack(side="left")

        # body
        body = tk.Frame(outer, bg=BG_CARD, padx=14, pady=10)
        body.pack(fill="both", expand=True)
        builder_fn(body)

    # ── File section ──────────────────────────────────────────────────────────

    def _build_file_section(self, parent):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x")

        entry = tk.Entry(
            row,
            textvariable=self.csv_path,
            font=FONT_MONO,
            bg=BG_ENTRY,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=FG_DIM,
            highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

        self._btn(row, "Browse CSV", self._browse_csv, ACCENT).pack(side="left")

        # Preview row count label (hidden until file is loaded)
        self.info_label = tk.Label(
            parent, text="", font=FONT_SMALL, bg=BG_CARD, fg=FG_DIM, anchor="w"
        )
        self.info_label.pack(fill="x", pady=(6, 0))

    # ── Format section ────────────────────────────────────────────────────────

    def _build_format_section(self, parent):
        fmt_row = tk.Frame(parent, bg=BG_CARD)
        fmt_row.pack(fill="x")

        for label, val in [("XML", "xml"), ("JSON", "json")]:
            rb = tk.Radiobutton(
                fmt_row,
                text=f"  {label}",
                variable=self.format_var,
                value=val,
                font=FONT_LABEL,
                bg=BG_CARD,
                fg=FG,
                selectcolor=BG_CARD,
                activebackground=BG_CARD,
                activeforeground=ACCENT,
                indicatoron=False,
                relief="flat",
                bd=0,
                padx=16,
                pady=6,
                highlightthickness=0,
                cursor="hand2",
                command=self._update_format_highlight,
            )
            rb.pack(side="left", padx=(0, 8))

        self.fmt_radios = fmt_row.winfo_children()
        self._update_format_highlight()

    def _update_format_highlight(self):
        """Visually highlight the selected format radio button."""
        chosen = self.format_var.get()
        labels = {"xml": "  XML", "json": "  JSON"}
        for widget in self.fmt_radios:
            if isinstance(widget, tk.Radiobutton):
                is_sel = (widget.cget("value") == chosen)
                widget.configure(
                    bg=ACCENT if is_sel else BG_ENTRY,
                    fg="#FFFFFF" if is_sel else FG,
                )

    # ── Action buttons ────────────────────────────────────────────────────────

    def _build_action_buttons(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=(0, 12))

        self._btn(frame, "⚙  Convert", self._convert, ACCENT).pack(
            side="left", padx=(0, 10), ipady=4, ipadx=10
        )
        self._btn(frame, "🗑  Clear", self._clear_all, BG_ENTRY).pack(
            side="left", padx=(0, 10)
        )
        self._btn(frame, "✕  Exit", self.destroy, BTN_EXIT_BG).pack(side="right")

    # ── Log section ───────────────────────────────────────────────────────────

    def _build_log_section(self, parent):
        self.log_text = tk.Text(
            parent,
            height=9,
            font=FONT_MONO,
            bg=BG_ENTRY,
            fg=FG,
            relief="flat",
            wrap="word",
            state="disabled",
            bd=0,
            highlightthickness=1,
            highlightbackground=FG_DIM,
            padx=8,
            pady=6,
        )
        self.log_text.pack(fill="both", expand=True)

        # Colour tags for the log
        self.log_text.tag_config("info",    foreground=FG)
        self.log_text.tag_config("success", foreground=SUCCESS)
        self.log_text.tag_config("warning", foreground=WARNING)
        self.log_text.tag_config("error",   foreground=ERROR)
        self.log_text.tag_config("dim",     foreground=FG_DIM)

        # Scrollbar
        sb = ttk.Scrollbar(parent, orient="vertical", command=self.log_text.yview)
        sb.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=sb.set)

    # ──────────────────────────────────────────────────────────────────────────
    # Helper: generic styled button
    # ──────────────────────────────────────────────────────────────────────────

    def _btn(self, parent, text: str, command, bg_color: str) -> tk.Button:
        b = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONT_BTN,
            bg=bg_color,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#FFFFFF",
        )
        b.bind("<Enter>", lambda e: b.configure(bg=ACCENT_DARK))
        b.bind("<Leave>", lambda e: b.configure(bg=bg_color))
        return b

    # ──────────────────────────────────────────────────────────────────────────
    # Logging helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _log(self, message: str, level: str = "info"):
        self.log_text.configure(state="normal")
        prefix = {"info": "  ℹ", "success": "  ✓", "warning": "  ⚠", "error": "  ✗", "dim": "   "}.get(level, "   ")
        self.log_text.insert("end", f"{prefix}  {message}\n", level)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_divider(self):
        self._log("─" * 55, "dim")

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        self.update_idletasks()

    # ──────────────────────────────────────────────────────────────────────────
    # Core actions
    # ──────────────────────────────────────────────────────────────────────────

    def _browse_csv(self):
        """Open a file dialog to select a CSV file and load it."""
        path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return

        self.csv_path.set(path)
        self._load_csv(path)

    def _load_csv(self, path: str):
        """Read the CSV into a DataFrame and update the UI."""
        self._log_divider()
        self._log(f"Loading: {os.path.basename(path)}")
        self._set_status("Reading CSV…")

        try:
            self.df = detect_and_read_csv(path)
        except RuntimeError as exc:
            self._log(str(exc), "error")
            self._set_status("Failed to load CSV.")
            messagebox.showerror("Load Error", str(exc))
            return

        rows, cols = self.df.shape
        self._log(f"Loaded successfully – {rows:,} rows × {cols} columns", "success")
        self._log(f"Columns: {', '.join(self.df.columns.tolist())}", "dim")
        self.info_label.configure(
            text=f"Loaded:  {rows:,} rows  ×  {cols} columns  |  {os.path.basename(path)}"
        )
        self._set_status(f"CSV loaded – {rows:,} rows × {cols} columns")

    def _convert(self):
        """Validate state, ask for save path, convert, and validate output."""
        # ── Guard: CSV loaded? ────────────────────────────────────────────────
        if self.df is None:
            messagebox.showwarning("No File", "Please browse and select a CSV file first.")
            return

        fmt = self.format_var.get()   # "xml" or "json"
        ext = f".{fmt}"

        # ── Ask where to save ─────────────────────────────────────────────────
        default_name = os.path.splitext(os.path.basename(self.csv_path.get()))[0] + ext
        save_path = filedialog.asksaveasfilename(
            title=f"Save {fmt.upper()} File",
            defaultextension=ext,
            initialfile=default_name,
            filetypes=[(f"{fmt.upper()} Files", f"*{ext}"), ("All Files", "*.*")],
        )
        if not save_path:
            return

        self._log_divider()
        self._log(f"Converting to {fmt.upper()}…")
        self._set_status(f"Converting to {fmt.upper()}…")

        # ── Perform conversion ────────────────────────────────────────────────
        try:
            if fmt == "xml":
                output_bytes = dataframe_to_xml(self.df)
            else:
                output_bytes = dataframe_to_json_bytes(self.df)

            with open(save_path, "wb") as fh:
                fh.write(output_bytes)

        except Exception as exc:  # noqa: BLE001
            self._log(f"Conversion failed: {exc}", "error")
            self._set_status("Conversion failed.")
            messagebox.showerror("Conversion Error", str(exc))
            return

        file_kb = len(output_bytes) / 1024
        self._log(f"Saved to: {save_path}", "success")
        self._log(f"File size: {file_kb:.1f} KB", "dim")

        # ── Validate output ───────────────────────────────────────────────────
        self._log("Validating output…")
        passed, detail = validate_output(self.df, save_path, fmt)
        if passed:
            self._log(detail, "success")
            self._set_status(f"{fmt.upper()} saved and validated ✓")
            messagebox.showinfo(
                "Conversion Complete",
                f"File saved successfully!\n\n{detail}\n\nPath:\n{save_path}",
            )
        else:
            self._log(detail, "warning")
            self._set_status("Saved – validation reported discrepancies.")
            messagebox.showwarning(
                "Validation Warning",
                f"File saved, but validation found discrepancies:\n\n{detail}\n\nPath:\n{save_path}",
            )

    def _clear_all(self):
        """Reset the application to its initial state."""
        self.df = None
        self.csv_path.set("")
        self.info_label.configure(text="")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._set_status("Cleared – select a CSV file to begin.")

    # ──────────────────────────────────────────────────────────────────────────
    # Window centering
    # ──────────────────────────────────────────────────────────────────────────

    def _centre_window(self):
        """Position the window in the centre of the screen."""
        self.update_idletasks()
        w, h = 760, 620
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")


# ═════════════════════════════════════════════════════════════════════════════
# Entry point
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = CSVConverterApp()
    app.mainloop()