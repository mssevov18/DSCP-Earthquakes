#!/usr/bin/env python3
import sys
from pathlib import Path
import tarfile
import gzip


def extract_all(source: Path, target: Path):
    """
    Extract each .tar in `source` into `target/<name>/`,
    then inside each output folder extract exactly the three .tar.gz
    into subdirs all.img/, kik/, knt/, and delete all archives.
    """
    print(f"[DEBUG] extract_all(source={source}, target={target})")
    if not source.is_dir():
        print(f"Source path is not a directory: {source}")
        sys.exit(1)
    target.mkdir(parents=True, exist_ok=True)
    for tf in sorted(source.glob("*.tar")):
        if tf.stat().st_size == 0:
            print(f"[!] Skipping empty archive {tf.name}")
            tf.unlink()
            continue
        name = tf.stem
        out_dir = target / name
        out_dir.mkdir(exist_ok=True, parents=True)

        print(f"[+] Extracting {tf.name} → {out_dir}")
        try:
            with tarfile.open(tf, "r") as tar:
                tar.extractall(path=out_dir)
        except tarfile.TarError as e:
            print(f"  [!] Failed to extract {tf.name}: {e}")
        finally:
            tf.unlink()  # always delete, even if extraction failed

        # Now extract exactly the .tar.gz files inside
        for gz in out_dir.glob("*.tar.gz"):
            nm = gz.name.lower()
            if ".all.img" in nm:
                sub = out_dir / "all.img"
            elif ".kik" in nm:
                sub = out_dir / "kik"
            elif ".knt" in nm:
                sub = out_dir / "knt"
            else:
                print(f"  [!] Skipping unknown archive {gz.name}")
                continue

            sub.mkdir(exist_ok=True)
            print(f"  ↳ {gz.name} → {sub}")
            try:
                with gzip.open(gz, "rb") as f_in:
                    with tarfile.open(fileobj=f_in) as inner:
                        inner.extractall(path=sub)
                gz.unlink()
            except Exception as e:
                print(f"    [!] Failed to extract {gz.name}: {e}")


def main():
    print(f"[DEBUG] argv = {sys.argv}")
    if len(sys.argv) != 3:
        print("Usage: eq_extract.py <SOURCE_DIR> <TARGET_DIR>")
        sys.exit(1)

    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve()
    extract_all(src, dst)


if __name__ == "__main__":
    main()
