"""
PDF-Kompressor für LLM-Nutzung
- Entfernt alle Bilder aus PDFs
- Ziel: unter 30 MB
- Fügt Suffix "_llm-optimized" zum Dateinamen hinzu
- Überspringt Dateien die bereits kleiner als 30 MB sind
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader, PdfWriter

BASE_DIR = Path(__file__).parent.parent
IMPORT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
SIZE_LIMIT_MB = 30
SUFFIX = "_llm-optimized"


def setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    logger = logging.getLogger("pdf-compressor")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Log-Datei: {log_file}")
    return logger


def compress_pdf(input_path: Path, output_path: Path) -> tuple[float, float]:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    images_removed = 0
    for page in reader.pages:
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
                images_removed += len(keys_to_delete)
        writer.add_page(page)

    for page in writer.pages:
        page.compress_content_streams()

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    size_before = input_path.stat().st_size / (1024 * 1024)
    size_after = output_path.stat().st_size / (1024 * 1024)
    return size_before, size_after, images_removed


def main():
    log = setup_logging()

    if not IMPORT_DIR.exists():
        log.error(f"Input-Ordner nicht gefunden: {IMPORT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    pdf_files = sorted(IMPORT_DIR.rglob("*.pdf"))
    if not pdf_files:
        log.warning("Keine PDF-Dateien im input-Ordner gefunden.")
        return

    log.info(f"Gefunden: {len(pdf_files)} PDF-Datei(en)")
    log.info("-" * 60)

    skipped = processed = errors = 0

    for pdf_path in pdf_files:
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        relative = pdf_path.relative_to(IMPORT_DIR)
        output_path = OUTPUT_DIR / relative.parent / (pdf_path.stem + SUFFIX + pdf_path.suffix)

        if size_mb < SIZE_LIMIT_MB:
            log.info(f"[SKIP]    {relative}  ({size_mb:.1f} MB)")
            skipped += 1
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"[PROCESS] {relative}  ({size_mb:.1f} MB) ...")

        try:
            size_before, size_after, images_removed = compress_pdf(pdf_path, output_path)
            reduction = (1 - size_after / size_before) * 100
            log.info(f"          {size_before:.1f} MB → {size_after:.1f} MB  (-{reduction:.0f}%)  Bilder entfernt: {images_removed}")

            if size_after >= SIZE_LIMIT_MB:
                log.warning(f"          Datei immer noch > {SIZE_LIMIT_MB} MB nach Komprimierung: {output_path.name}")

            processed += 1
        except Exception as e:
            log.error(f"          FEHLER bei {relative}: {e}", exc_info=True)
            errors += 1

    log.info("-" * 60)
    log.info(f"Fertig — verarbeitet: {processed}, übersprungen: {skipped}, Fehler: {errors}")
    log.info(f"Ausgabe-Dateien in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
