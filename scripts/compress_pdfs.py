"""
PDF-Kompressor für LLM-Nutzung
- Entfernt alle Bilder aus PDFs
- Ziel: unter 30 MB
- Fügt Suffix "_llm-optimized" zum Dateinamen hinzu
- Überspringt Dateien die bereits kleiner als 30 MB sind
"""

import os
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter

BASE_DIR = Path(__file__).parent.parent
IMPORT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
SIZE_LIMIT_MB = 30
SIZE_LIMIT_BYTES = SIZE_LIMIT_MB * 1024 * 1024
SUFFIX = "_llm-optimized"


def compress_pdf(input_path: Path, output_path: Path) -> tuple[float, float]:
    """Entfernt Bilder und komprimiert die PDF. Gibt (vorher_mb, nachher_mb) zurück."""
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        # Bilder aus den Ressourcen der Seite entfernen
        if "/Resources" in page:
            resources = page["/Resources"]
            if "/XObject" in resources:
                xobject = resources["/XObject"].get_object()
                keys_to_delete = [
                    key for key, obj in xobject.items()
                    if obj.get_object().get("/Subtype") == "/Image"
                ]
                for key in keys_to_delete:
                    del xobject[key]

        writer.add_page(page)

    # Komprimierung aktivieren
    for page in writer.pages:
        page.compress_content_streams()

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    size_before = input_path.stat().st_size / (1024 * 1024)
    size_after = output_path.stat().st_size / (1024 * 1024)
    return size_before, size_after


def main():
    if not IMPORT_DIR.exists():
        print(f"Input-Ordner nicht gefunden: {IMPORT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    pdf_files = sorted(IMPORT_DIR.rglob("*.pdf"))
    if not pdf_files:
        print("Keine PDF-Dateien im input-Ordner gefunden.")
        return

    print(f"Gefunden: {len(pdf_files)} PDF-Datei(en)\n")

    for pdf_path in pdf_files:
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        # Unterordner-Struktur im output beibehalten
        relative = pdf_path.relative_to(IMPORT_DIR)
        output_path = OUTPUT_DIR / relative.parent / (pdf_path.stem + SUFFIX + pdf_path.suffix)

        if size_mb < SIZE_LIMIT_MB:
            print(f"[SKIP]    {relative}  ({size_mb:.1f} MB < {SIZE_LIMIT_MB} MB)")
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[PROCESS] {relative}  ({size_mb:.1f} MB)", end=" ... ", flush=True)

        try:
            size_before, size_after = compress_pdf(pdf_path, output_path)
            reduction = (1 - size_after / size_before) * 100
            status = "OK" if size_after < SIZE_LIMIT_MB else "WARNUNG: immer noch > 30 MB"
            print(f"{size_before:.1f} MB → {size_after:.1f} MB  (-{reduction:.0f}%)  [{status}]")
        except Exception as e:
            print(f"FEHLER: {e}")

    print(f"\nFertig. Ausgabe-Dateien in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
