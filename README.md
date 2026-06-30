# LLM PDF Compressor

Komprimiert PDF-Dateien auf unter 30 MB für die Nutzung mit Large Language Models (LLMs).

Bilder werden vollständig entfernt, da sie für die Textverarbeitung durch LLMs irrelevant sind. Dateien, die bereits kleiner als 30 MB sind, werden übersprungen.

## Voraussetzungen

- Python 3.10+
- `pypdf` Bibliothek

```bash
pip install pypdf
```

## Ordnerstruktur

```
llm-pdf-compressor/
├── compress_pdfs.bat       # Windows: Doppelklick zum Starten
├── input/                  # PDFs hier ablegen (Unterordner werden unterstützt)
├── output/                 # Komprimierte PDFs landen hier
└── scripts/
    └── compress_pdfs.py    # Haupt-Script
```

## Verwendung

### Windows

Doppelklick auf `compress_pdfs.bat`

### Kommandozeile

```bash
python scripts/compress_pdfs.py
```

## Verhalten

| Dateigröße | Aktion |
|---|---|
| < 30 MB | `[SKIP]` – wird nicht verarbeitet |
| ≥ 30 MB | Bilder entfernen, komprimieren, als `*_llm-optimized.pdf` speichern |

Unterordner im `input/` Ordner werden rekursiv durchsucht und die Ordnerstruktur im `output/` Ordner gespiegelt.

### Beispiel-Output

```
Gefunden: 7 PDF-Datei(en)

[SKIP]    Cornell und Schwertmann - 2003 - The Iron Oxides.pdf  (21.5 MB < 30 MB)
[PROCESS] Dixon et al. - 1989 - Minerals in soil environments.pdf  (137.2 MB) ... 137.2 MB → 4.1 MB  (-97%)  [OK]
[PROCESS] Joisten et al. - 2023 - Böden Deutschlands.pdf  (795.2 MB) ... 795.2 MB → 12.3 MB  (-98%)  [OK]

Fertig. Ausgabe-Dateien in: C:\...\output
```

## Hinweise

- Die Original-Dateien im `input/` Ordner werden **nicht verändert**
- Falls eine PDF nach der Komprimierung immer noch > 30 MB ist (z. B. sehr große reine Text-PDFs), erscheint eine `WARNUNG` in der Ausgabe
- Bereits komprimierte Dateien (`*_llm-optimized.pdf`) im `output/` Ordner werden beim nächsten Durchlauf überschrieben
