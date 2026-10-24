# Convert JSON to Zefania XML

`convert_json_to_zefania.py` converts the churchDB database JSON export used by `bblfnt.json` into a Zefania XML file with the same core structure as `FNT.xml`. It uses only Python's standard library.

## Double-click workflow

Double-click `convert_json_to_zefania.py`, select a `.json` file, and the script saves an `.xml` file beside it with the same base name. For example, `bblfnt.json` produces `bblfnt.xml`. If that XML already exists, the script asks before replacing it. Cancel the file picker to exit.

Python must be installed and associated with `.py` files for double-clicking to work. If double-clicking opens the file in an editor or does nothing, use PowerShell from this folder:

```powershell
python .\convert_json_to_zefania.py .\bblfnt.json
```

You can also specify the output path explicitly:

```powershell
python .\convert_json_to_zefania.py .\bblfnt.json .\bblfnt.xml
```

## Expected JSON structure

The script expects the database export shape used by `bblfnt.json`: a top-level `columns` array describing the fields, plus a `rows` array containing each record as an array. It reads:

- `ari`: book number, chapter, and verse, such as `1:1:1`
- `title`: English Bible book title, such as `GENESIS` or `1ST KINGS`
- `verse`: verse text

The extra `name` column is ignored. This converter is for that database export format, not arbitrary JSON layouts.

The output uses `<BIBLE>` → `<BIBLEBOOK>` → `<CHAPTER>` → `<VERS>`, matching the core structure in `FNT.xml`. Book numbers come from the first part of `ari`; chapters and verses are sorted numerically. Titles like `1ST KINGS` become `bname="1 Kings"` and `bsname="1kings"`.

The source JSON has 64 unique books, with book IDs 8 and 9 absent. The converter preserves the IDs in `ari`, so those missing books remain gaps in `bnumber` rather than being renumbered.
