#!/usr/bin/env python3
"""Convert a CSV of Bible verses to a basic Zefania XML Bible."""

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path


def positive_int(value: str, column: str, row_number: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"row {row_number}: {column} must be a whole number; got {value!r}")
    if number < 1:
        raise ValueError(f"row {row_number}: {column} must be at least 1; got {number}")
    return number


def convert(args: argparse.Namespace) -> None:
    # Keep books in first-seen order, and sort chapters/verses numerically.
    books = OrderedDict()
    with args.input.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=args.delimiter)
        if not reader.fieldnames:
            raise ValueError("the CSV is empty or has no header row")

        columns = {name: getattr(args, name + "_column") for name in ("book", "chapter", "verse", "text")}
        missing = [column for column in columns.values() if column not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"missing CSV column(s): {', '.join(missing)}. "
                f"Available columns: {', '.join(reader.fieldnames)}"
            )

        seen_rows = 0
        for row_number, row in enumerate(reader, start=2):
            seen_rows += 1
            book_name = (row.get(columns["book"]) or "").strip()
            text = row.get(columns["text"])
            if not book_name:
                raise ValueError(f"row {row_number}: book name is blank")
            if text is None or not text.strip():
                raise ValueError(f"row {row_number}: verse text is blank")

            chapter_num = positive_int(row.get(columns["chapter"]), columns["chapter"], row_number)
            verse_num = positive_int(row.get(columns["verse"]), columns["verse"], row_number)
            chapter_map = books.setdefault(book_name, {})
            verse_map = chapter_map.setdefault(chapter_num, {})
            if verse_num in verse_map:
                raise ValueError(
                    f"row {row_number}: duplicate verse {book_name} {chapter_num}:{verse_num}"
                )
            verse_map[verse_num] = text.strip()

    if not books:
        raise ValueError("the CSV contains a header but no verse rows")

    # FNT.xml uses the legacy Zefania root element named BIBLE.
    root = ET.Element("BIBLE")
    for book_number, (book_name, chapters) in enumerate(books.items(), start=1):
        book = ET.SubElement(
            root,
            "BIBLEBOOK",
            {
                "bnumber": str(book_number),
                "bname": book_name,
                "bsname": "".join(book_name.lower().split()),
            },
        )
        for chapter_number in sorted(chapters):
            chapter = ET.SubElement(book, "CHAPTER", {"cnumber": str(chapter_number)})
            for verse_number in sorted(chapters[chapter_number]):
                verse = ET.SubElement(chapter, "VERS", {"vnumber": str(verse_number)})
                verse.text = chapters[chapter_number][verse_number]

    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a CSV with book, chapter, verse, and text columns to Zefania XML."
    )
    parser.add_argument("input", type=Path, help="source CSV file")
    parser.add_argument("output", type=Path, help="destination XML file")
    parser.add_argument("--book-column", default="book", help="CSV header for book name (default: book)")
    parser.add_argument("--chapter-column", default="chapter", help="CSV header for chapter (default: chapter)")
    parser.add_argument("--verse-column", default="verse", help="CSV header for verse (default: verse)")
    parser.add_argument("--text-column", default="text", help="CSV header for verse text (default: text)")
    parser.add_argument("--delimiter", default=",", help="one-character CSV delimiter (default: comma)")
    args = parser.parse_args()
    if len(args.delimiter) != 1:
        parser.error("--delimiter must be exactly one character")
    return args


def main() -> int:
    args = parse_args()
    try:
        convert(args)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Created {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
