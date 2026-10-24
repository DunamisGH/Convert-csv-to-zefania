#!/usr/bin/env python3
"""Convert a conforming, Zefania-shaped JSON document to Zefania XML."""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def required_object(value: object, description: str, row: int) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{description} {row} must be a JSON object")
    return value


def required_positive_int(value: object, field: str, description: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{description}: {field} must be a positive whole number")
    return value


def required_text(value: object, field: str, description: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{description}: {field} must be a non-empty string")
    return value.strip()


def convert(args: argparse.Namespace) -> None:
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}")

    if not isinstance(data, dict) or not isinstance(data.get("books"), list):
        raise ValueError("top level must be an object with a 'books' array")
    if not data["books"]:
        raise ValueError("the 'books' array is empty")

    root = ET.Element("BIBLE")
    seen_book_numbers = set()
    seen_abbreviations = set()
    for book_index, value in enumerate(data["books"], start=1):
        book_data = required_object(value, "book", book_index)
        description = f"book {book_index}"
        number = required_positive_int(book_data.get("bnumber"), "bnumber", description)
        name = required_text(book_data.get("bname"), "bname", description)
        abbreviation = required_text(book_data.get("bsname"), "bsname", description)
        if number in seen_book_numbers:
            raise ValueError(f"{description}: duplicate bnumber {number}")
        if abbreviation in seen_abbreviations:
            raise ValueError(f"{description}: duplicate bsname {abbreviation!r}")
        seen_book_numbers.add(number)
        seen_abbreviations.add(abbreviation)

        chapters_data = book_data.get("chapters")
        if not isinstance(chapters_data, list) or not chapters_data:
            raise ValueError(f"{description}: 'chapters' must be a non-empty array")
        book = ET.SubElement(
            root,
            "BIBLEBOOK",
            {"bnumber": str(number), "bname": name, "bsname": abbreviation},
        )
        seen_chapters = set()
        for chapter_index, chapter_value in enumerate(chapters_data, start=1):
            chapter_data = required_object(chapter_value, f"{description} chapter", chapter_index)
            chapter_description = f"{description}, chapter {chapter_index}"
            chapter_number = required_positive_int(
                chapter_data.get("cnumber"), "cnumber", chapter_description
            )
            if chapter_number in seen_chapters:
                raise ValueError(f"{chapter_description}: duplicate cnumber {chapter_number}")
            seen_chapters.add(chapter_number)
            verses_data = chapter_data.get("verses")
            if not isinstance(verses_data, list) or not verses_data:
                raise ValueError(f"{chapter_description}: 'verses' must be a non-empty array")
            chapter = ET.SubElement(book, "CHAPTER", {"cnumber": str(chapter_number)})
            seen_verses = set()
            for verse_index, verse_value in enumerate(verses_data, start=1):
                verse_data = required_object(verse_value, f"{chapter_description} verse", verse_index)
                verse_description = f"{chapter_description}, verse record {verse_index}"
                verse_number = required_positive_int(
                    verse_data.get("vnumber"), "vnumber", verse_description
                )
                text = required_text(verse_data.get("text"), "text", verse_description)
                if verse_number in seen_verses:
                    raise ValueError(f"{chapter_description}: duplicate vnumber {verse_number}")
                seen_verses.add(verse_number)
                verse = ET.SubElement(chapter, "VERS", {"vnumber": str(verse_number)})
                verse.text = text

    ET.indent(root, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.output, encoding="utf-8", xml_declaration=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Zefania-shaped JSON document to Zefania XML."
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
            title="Choose a Zefania-shaped JSON file",
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
