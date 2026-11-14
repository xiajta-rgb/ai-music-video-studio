from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

SUPPORTED = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "private_media" / "qq-fantasy"
CATALOG = DEST / "catalog.json"


def main():
    parser = argparse.ArgumentParser(description="导入用户合法取得的 QQ自由幻想地图音乐文件")
    parser.add_argument("source", type=Path, help="包含音频文件的本地目录")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"目录不存在：{source}")
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for src in sorted(source.rglob("*")):
        if not src.is_file() or src.suffix.lower() not in SUPPORTED:
            continue
        target = DEST / src.name
        shutil.copy2(src, target)
        records.append({"file": target.name, "map": src.stem, "format": src.suffix.lower().lstrip(".")})
    CATALOG.write_text(json.dumps({"source": "user-provided-local-files", "tracks": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Imported {len(records)} audio files to {DEST}")


if __name__ == "__main__":
    main()
