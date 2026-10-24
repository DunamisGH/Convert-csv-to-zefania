# Convert CSV to Zefania XML

This guide uses `convert_csv_to_zefania.py` to turn a CSV containing Bible verses into a basic Zefania XML file. It uses only Python's standard library; no package installation is needed.

## 1. Prepare your CSV

The default header names are `book`, `chapter`, `verse`, and `text`. Each data row should represent one verse:

```csv
book,chapter,verse,text
Genesis,1,1,In the beginning God created the heaven and the earth.
Genesis,1,2,And the earth was without form, and void.
Genesis,2,1,Thus the heavens and the earth were finished.
Exodus,1,1,Now these are the names of the children of Israel.
```

CSV handles commas in verse text when the field is quoted. For example:

```csv
Genesis,1,2,"And the earth was without form, and void."
```

Save the file as UTF-8, for example `verses.csv`. A UTF-8 file with a BOM (often produced by Excel) is also accepted by default.

## 2. Run the converter

Open a terminal in this folder and run:

```powershell
python .\convert_csv_to_zefania.py .\verses.csv .\bible.xml
```

If `python` is not recognized on Windows, try `py` instead:

```powershell
py .\convert_csv_to_zefania.py .\verses.csv .\bible.xml
```

The XML output will contain books in the order they first appear in the CSV. Chapters and verses are sorted numerically. The converter stops with a row-specific error if a required value is missing, a chapter or verse number is not a positive integer, or a verse is duplicated.

## 3. Use different CSV header names

For a CSV with headers `Book Name,Chapter No,Verse No,Verse Text`, map them like this:

```powershell
python .\convert_csv_to_zefania.py .\verses.csv .\bible.xml --book-column "Book Name" --chapter-column "Chapter No" --verse-column "Verse No" --text-column "Verse Text"
```

For a semicolon-separated CSV, add `--delimiter ";"`:

```powershell
python .\convert_csv_to_zefania.py .\verses.csv .\bible.xml --delimiter ";"
```

## Output shape

The output groups verses under books and chapters and uses the same core shape as `FNT.xml` (`<BIBLE>` root, followed by `<BIBLEBOOK>`, `<CHAPTER>`, and `<VERS>`):

```xml
<?xml version='1.0' encoding='utf-8'?>
<BIBLE>
  <BIBLEBOOK bnumber="1" bname="Genesis" bsname="genesis">
    <CHAPTER cnumber="1">
      <VERS vnumber="1">In the beginning God created the heaven and the earth.</VERS>
    </CHAPTER>
  </BIBLEBOOK>
</BIBLE>
```

This is a minimal conversion. `bnumber` follows the order of books in your CSV. `bname` uses the CSV book name, while `bsname` is derived by lowercasing it and removing spaces (for example, `1 Kings` becomes `1kings`). `FNT.xml` uses this same abbreviation style. Its books are in a particular order, so put your CSV rows in the desired book order. Some Bible readers also require extra metadata; check the requirements of your target app if it rejects the file.
