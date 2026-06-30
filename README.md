# llm-pdf-compressor

Strips embedded images from scientific PDF textbooks so they can be uploaded to Claude Projects (30 MB file limit). Text content and structure are fully preserved — images are irrelevant for LLM text processing.

## Features

- Recursively scans an `input/` directory for PDF files
- Skips files already under the 30 MB size limit
- Removes embedded images (irrelevant for text-based LLM processing)
- Preserves subdirectory structure in `output/`
- Writes timestamped log files to `logs/`

## Requirements

- Python 3.10+

## Installation

```bash
git clone https://github.com/blauschiefer/llm-pdf-compressor.git
cd llm-pdf-compressor
pip install -r requirements.txt
```

## Usage

Place PDF files in the `input/` directory, then run:

**Windows**

```bat
compress.bat
```

**Command line**

```bash
python src/compress.py
```

Compressed files are written to `output/` with the suffix `_llm-optimized`.

## Project Structure

```
llm-pdf-compressor/
├── src/
│   └── compress.py       # Main script
├── input/                # Place source PDFs here (gitignored)
├── output/               # Compressed PDFs are written here (gitignored)
├── logs/                 # Timestamped log files (gitignored)
├── compress.bat          # Windows launcher
├── requirements.txt
└── README.md
```

## Example Output

```
2026-06-30 10:45:00  INFO      Found 7 PDF file(s)
2026-06-30 10:45:00  INFO      ------------------------------------------------------------
2026-06-30 10:45:00  INFO      [SKIP]    Cornell - 2003 - The Iron Oxides.pdf  (21.5 MB)
2026-06-30 10:45:01  INFO      [PROCESS] Dixon - 1989 - Minerals in soil environments.pdf  (137.2 MB) ...
2026-06-30 10:45:12  INFO                137.2 MB → 4.1 MB  (-97%)  images removed: 843
2026-06-30 10:45:12  INFO      ------------------------------------------------------------
2026-06-30 10:45:12  INFO      Done — processed: 1, skipped: 1, errors: 0
```

## License

MIT
