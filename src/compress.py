"""
LLM PDF Compressor
Strips embedded images from PDF files so they can be uploaded to Claude Projects (30 MB limit).
Text content and structure are fully preserved.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import pikepdf

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
SIZE_LIMIT_MB = 30
OUTPUT_SUFFIX = "_llm-optimized"


def setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    logger = logging.getLogger("llm-pdf-compressor")
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

    logger.info(f"Log file: {log_file}")
    return logger


def strip_images(input_path: Path, output_path: Path) -> tuple[float, float, int]:
    """Remove all embedded images from a PDF. Returns (size_before_mb, size_after_mb, images_removed)."""
    images_removed = 0

    with pikepdf.open(str(input_path)) as pdf:
        for page in pdf.pages:
            resources = page.get("/Resources", {})
            xobjects = resources.get("/XObject", {})
            keys_to_delete = [
                key for key in xobjects
                if xobjects[key].get("/Subtype") == "/Image"
            ]
            for key in keys_to_delete:
                del xobjects[key]
            images_removed += len(keys_to_delete)

        pdf.save(str(output_path))

    size_before = input_path.stat().st_size / (1024 * 1024)
    size_after = output_path.stat().st_size / (1024 * 1024)
    return size_before, size_after, images_removed


def main():
    log = setup_logging()

    if not INPUT_DIR.exists():
        log.error(f"Input directory not found: {INPUT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    pdf_files = sorted(INPUT_DIR.rglob("*.pdf"))
    if not pdf_files:
        log.warning("No PDF files found in input directory.")
        return

    log.info(f"Found {len(pdf_files)} PDF file(s)")
    log.info("-" * 60)

    skipped = processed = errors = 0

    for pdf_path in pdf_files:
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        relative = pdf_path.relative_to(INPUT_DIR)
        output_path = OUTPUT_DIR / relative.parent / (pdf_path.stem + OUTPUT_SUFFIX + pdf_path.suffix)

        if size_mb < SIZE_LIMIT_MB:
            log.info(f"[SKIP]    {relative}  ({size_mb:.1f} MB — already under {SIZE_LIMIT_MB} MB)")
            skipped += 1
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"[PROCESS] {relative}  ({size_mb:.1f} MB) ...")

        try:
            size_before, size_after, images_removed = strip_images(pdf_path, output_path)
            reduction = (1 - size_after / size_before) * 100
            log.info(f"          {size_before:.1f} MB → {size_after:.1f} MB  (-{reduction:.0f}%)  images removed: {images_removed}")

            if size_after >= SIZE_LIMIT_MB:
                log.warning(f"          Still exceeds {SIZE_LIMIT_MB} MB after stripping: {output_path.name}")

            processed += 1
        except Exception as e:
            log.error(f"          Failed to process {relative}: {e}", exc_info=True)
            errors += 1

    log.info("-" * 60)
    log.info(f"Done — processed: {processed}, skipped: {skipped}, errors: {errors}")
    log.info(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
