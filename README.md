# Codeccurlew

Read-only text encoding checks: BOM metadata, strict decoding, character counts and CRLF/bare-LF/bare-CR counts. No text conversion or content preview. Python 3.9+, standard library only.

## Run locally

Published in a private GitHub repository. Download its ZIP while signed into the owner account, extract it and open a terminal inside the source folder. Not verified as store-installed.

```text
python3 codeccurlew.py
python3 codeccurlew.py notes.txt
python3 codeccurlew.py notes.txt --encoding utf-16-le
python3 codeccurlew.py notes.txt --output report.json
python3 -m unittest -v
bash app-store.sh install
bash app-store.sh run
```

Auto mode chooses a recognized UTF-8/16/32 BOM, otherwise defaults to UTF-8. It does not detect an unknown encoding. Successful decoding is not proof of intended encoding: Latin-1 accepts every byte, ASCII bytes fit many encodings, and UTF-16 bytes can sometimes decode as UTF-8 with NULs. NUL counts are descriptive, not a binary-file verdict.

Explicit choices: utf-8, utf-8-sig, utf-16, utf-16-le/be, utf-32, utf-32-le/be, ascii, latin-1. Generic utf-16/32 require a matching BOM; choose endian-specific codecs for BOM-less data. Explicit endian-specific codecs can preserve a BOM as a character. An explicit encoding overrides BOM selection but the BOM metadata remains reported. No replacement characters are inserted to conceal errors.

Counts apply to the decoded text after that codec's BOM handling. CRLF counts as one pair; bare CR/LF exclude pairs. Unicode NEL/U+2028/U+2029 count separately. No inferred edit history or original platform. An empty file decodes as zero characters; decode failure returns metadata/error with no invented counts.

Regular files only, max 8 MiB, sequential non-atomic read; use stable copies. Reports refuse overwrite, including the source. No file content copied into reports, but counts/encoding can still be private. No network, history, automatic repair or conversion. CLI exits 0 decoded, 1 decode failure, 2 input/output error. Root marker/version files opt in to store integration. The current public-only Pi App Store cannot discover private repositories; authenticated store support is not verified.

16 tests cover BOM order, exact decoding, explicit overrides, BOM-less endian handling, newline styles, NULs, Unicode separators, source preservation, FIFO rejection and CLI. Linux tested; real Pi/non-Linux untested.
