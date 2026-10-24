# Convert conforming JSON to Zefania XML

`convert_json_to_zefania.py` converts a JSON document with the structure below into Zefania XML using the same core elements as `FNT.xml`. Prepare your JSON in this format before running the script. It does not read the churchDB database export format.

## Required JSON structure

The JSON must have a top-level `books` array. Each book needs `bnumber`, `bname`, `bsname`, and a `chapters` array. Each chapter needs `cnumber` and a `verses` array. Each verse needs `vnumber` and `text`.

```json
{
  "books": [
    {
      "bnumber": 1,
      "bname": "Genesis",
      "bsname": "genesis",
      "chapters": [
        {
          "cnumber": 1,
          "verses": [
            { "vnumber": 1, "text": "In the beginning God created the heaven and the earth." },
            { "vnumber": 2, "text": "And the earth was without form, and void." }
          ]
        },
        {
          "cnumber": 2,
          "verses": [
            { "vnumber": 1, "text": "Thus the heavens and the earth were finished." }
          ]
        }
      ]
    }
  ]
}
```

Use positive whole numbers for all number fields. `bnumber` should match the numbering expected by the Bible app; `bname` is the displayed book name; `bsname` is the short book identifier used by the app. Book, chapter, and verse numbers must be unique at their respective level. The script keeps the order of books, chapters, and verses from the JSON.

## Double-click workflow

Double-click `convert_json_to_zefania.py`, select a conforming `.json` file, and the script saves an `.xml` file beside it with the same base name. For example, `FNT.json` produces `FNT.xml`. If that XML already exists, the script asks before replacing it. Cancel the file picker to exit.

Python must be installed and associated with `.py` files for double-clicking to work. If double-clicking opens the file in an editor or does nothing, run it from PowerShell in this folder:

```powershell
python .\convert_json_to_zefania.py .\FNT.json
```

You can specify a different output path if needed:

```powershell
python .\convert_json_to_zefania.py .\FNT.json .\output.xml
```

The resulting XML uses `<BIBLE>` → `<BIBLEBOOK>` → `<CHAPTER>` → `<VERS>`. `bnumber`, `bname`, and `bsname` are copied from the JSON fields.
