#!/usr/bin/env python3
"""Convert a churchDB SQLite JSON table export to basic Zefania XML."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def positive_int(value: object, description: str, row_number: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"row {row_number}: invalid {description}: {value!r}")
    if number < 1:
        raise ValueError(f"row {row_number}: {description} must be at least 1; got {number}")
    return number


def book_name(title: str) -> str:
    """Convert titles such as '1ST KINGS' to the FNT-style '1 Kings'."""
    title = title.strip()
    title = re.sub(r"^(1ST|2ND|3RD)\b", lambda match: match.group(0)[0], title, flags=re.IGNORECASE)
    return " ".join(word[:1].upper() + word[1:].lower() for word in title.split())


def convert(args: argparse.Namespace) -> None:
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}")

    if not isinstance(data, dict) or not isinstance(data.get("columns"), list) or not isinstance(data.get("rows"), list):
        raise ValueError("expected a database JSON export containing 'columns' and 'rows' arrays")

    columns = [column.get("name") if isinstance(column, dict) else None for column in data["columns"]]
    required = ("ari", "title", "verse")
    missing = [name for name in required if name not in columns]
    if missing:
        raise ValueError(f"missing required JSON column(s): {', '.join(missing)}")
    indexes = {name: columns.index(name) for name in required}

    # Key by source book number so chapters/verses from interleaved rows regroup correctly.
    books = {}
    for row_number, row in enumerate(data["rows"], start=1):
        if not isinstance(row, list) or len(row) < len(columns):
            raise ValueError(f"row {row_number}: row does not match the JSON columns")
        reference = row[indexes["ari"]]
        title = row[indexes["title"]]
        text = row[indexes["verse"]]
        if not isinstance(reference, str) or not isinstance(title, str) or not isinstance(text, str):
            raise ValueError(f"row {row_number}: ari, title, and verse must be strings")
        parts = reference.split(":")
        if len(parts) != 3:
            raise ValueError(f"row {row_number}: expected ari in book:chapter:verse form; got {reference!r}")
        book_number = positive_int(parts[0], "book number in ari", row_number)
        chapter_number = positive_int(parts[1], "chapter number in ari", row_number)
        verse_number = positive_int(parts[2], "verse number in ari", row_number)
        if not title.strip() or not text.strip():
            raise ValueError(f"row {row_number}: title and verse text cannot be blank")

        normalized_name = book_name(title)
        entry = books.setdefault(book_number, {"name": normalized_name, "chapters": {}})
        if entry["name"] != normalized_name:
            raise ValueError(
                f"row {row_number}: book number {book_number} has conflicting titles "
                f"{entry['name']!r} and {normalized_name!r}"
            )
        chapter = entry["chapters"].setdefault(chapter_number, {})
        if verse_number in chapter:
            raise ValueError(f"row {row_number}: duplicate verse {normalized_name} {chapter_number}:{verse_number}")
        chapter[verse_number] = text.strip()

    if not books:
        raise ValueError("the JSON export contains no verse rows")

    root = ET.Element("BIBLE")
    for book_number in sorted(books):
        entry = books[book_number]
        name = entry["name"]
        book = ET.SubElement(
            root,
            "BIBLEBOOK",
            {"bnumber": str(book_number), "bname": name, "bsname": "".join(name.lower().split())},
        )
        for chapter_number in sorted(entry["chapters"]):
            chapter = ET.SubElement(book, "CHAPTER", {"cnumber": str(chapter_number)})
            for verse_number in sorted(entry["chapters"][chapter_number]):
                verse = ET.SubElement(chapter, "VERS", {"vnumber": str(verse_number)})
                verse.text = entry["chapters"][chapter_number][verse_number]

    ET.indent(root, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.output, encoding="utf-8", xml_declaration=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a churchDB database JSON export to Zefania XML."
    )
    parser.add_argument("input", type=Path, nargs="?", help="source JSON file")
    parser.add_argument("output", type=Path, nargs="?", help="destination XML file")
    args = parser.parse_args()
    if args.input is None and args.output is not None:
        parser.error("provide an input path before the output path")
    return args


def run_file_picker(args: argparse.Namespace) -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print("The file picker needs tkinter. Run the script from a terminal and provide input and output paths.", file=sys.stderr)
        return 1

    window = tk.Tk()
    window.withdraw()
    window.update()
    try:
        selected = filedialog.askopenfilename(
            title="Choose a Bible database JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not selected:
            return 0
        args.input = Path(selected)
        args.output = args.output or args.input.with_suffix(".xml")
        if args.output.exists() and not messagebox.askyesno(
            "Replace existing XML?", f"{args.output.name} already exists. Replace it?", parent=window
        ):
            return 0
        convert(args)
        messagebox.showinfo("Conversion complete", f"Created:\n{args.output}", parent=window)
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        messagebox.showerror("Conversion failed", str(error), parent=window)
        return 1
    finally:
        window.destroy()


def main() -> int:
    args = parse_args()
    if args.input is None:
        return run_file_picker(args)
    if args.output is None:
        args.output = args.input.with_suffix(".xml")
    try:
        convert(args)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Created {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
