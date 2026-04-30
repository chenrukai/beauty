from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import shutil

from PIL import Image, ImageChops


ROOT = Path(r"D:\beauty")
DOCX = next(p for p in ROOT.glob("*_tmp_fix.docx") if not p.name.startswith("~$"))
FALLBACK = DOCX.with_name(DOCX.stem + "_第五章流程图居中" + DOCX.suffix)
TARGETS = {
    "word/media/image11.png",
    "word/media/image12.png",
    "word/media/image13.png",
    "word/media/image14.png",
    "word/media/image15.png",
    "word/media/image16.png",
}
BG = "#ffffff"


def recenter_png(data: bytes, padding: int = 36) -> bytes:
    src = Image.open(BytesIO(data)).convert("RGB")
    bg = Image.new("RGB", src.size, BG)
    bbox = ImageChops.difference(src, bg).getbbox()
    if not bbox:
        return data
    x1, y1, x2, y2 = bbox
    crop = src.crop((
        max(0, x1 - padding),
        max(0, y1 - padding),
        min(src.width, x2 + padding),
        min(src.height, y2 + padding),
    ))
    canvas = Image.new("RGB", src.size, BG)
    px = max(0, (canvas.width - crop.width) // 2)
    py = max(0, (canvas.height - crop.height) // 2)
    canvas.paste(crop, (px, py))
    out = BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def rewrite_to(output_path: Path) -> None:
    tmp = output_path.with_suffix(".recenter.tmp")
    shutil.copy2(DOCX, tmp)
    with ZipFile(tmp) as zin, ZipFile(output_path, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in TARGETS:
                data = recenter_png(data)
            zout.writestr(info, data)
    tmp.unlink(missing_ok=True)


def main() -> None:
    try:
        rewrite_to(DOCX)
        print("Updated", DOCX)
    except PermissionError:
        rewrite_to(FALLBACK)
        print("Locked source, wrote fallback", FALLBACK)


if __name__ == "__main__":
    main()
