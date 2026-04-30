from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import shutil
import subprocess


ROOT = Path(r"D:\beauty")
DOCX = ROOT / "毕业论文_最终稿_规范达标版 - 副本._tmp_fix_第五章标准流程图.docx"
DRAWIO_DIR = ROOT / "final_assets" / "thesis_copy_fix" / "drawio"
DRAWIO_SCRIPTS = Path(r"C:\Users\YLDN\.codex\skills\drawio\scripts")
CLI = DRAWIO_SCRIPTS / "cli.js"

TARGETS = {
    "图3-2-系统数据流图": "word/media/image3.png",
    "图4-2-系统功能模块设计图": "word/media/image7.png",
    "图5-3-知识管理流程图": "word/media/image13.png",
    "图5-4-文件处理流程图": "word/media/image14.png",
    "图5-5-知识图谱流程图": "word/media/image15.png",
    "图5-6-智能问答流程图": "word/media/image16.png",
}


def export_svg_and_png(stem: str) -> bytes:
    yaml_path = DRAWIO_DIR / f"{stem}.yaml"
    svg_path = DRAWIO_DIR / f"{stem}.svg"
    png_path = DRAWIO_DIR / f"{stem}.png"
    subprocess.run(
        ["node", str(CLI), str(yaml_path), str(svg_path), "--validate"],
        cwd=str(DRAWIO_SCRIPTS),
        check=True,
    )
    render_js = DRAWIO_SCRIPTS / "_render_svg_to_png.mjs"
    if not render_js.exists():
        render_js.write_text(
            """import { readFileSync, writeFileSync } from 'node:fs';\n"""
            """import { Resvg } from '@resvg/resvg-js';\n"""
            """const [svgPath, pngPath, widthArg] = process.argv.slice(2);\n"""
            """const svg = readFileSync(svgPath);\n"""
            """const width = Number(widthArg || 2400);\n"""
            """const resvg = new Resvg(svg, { fitTo: { mode: 'width', value: width }, background: 'white' });\n"""
            """const png = resvg.render().asPng();\n"""
            """writeFileSync(pngPath, png);\n""",
            encoding="utf-8",
        )
    subprocess.run(
        ["node", str(render_js), str(svg_path), str(png_path), "2400"],
        cwd=str(DRAWIO_SCRIPTS),
        check=True,
    )
    return png_path.read_bytes()


def main() -> None:
    media_map = {target: export_svg_and_png(stem) for stem, target in TARGETS.items()}
    tmp = DOCX.with_suffix(".whitepng.tmp")
    shutil.copy2(DOCX, tmp)
    with ZipFile(tmp) as zin, ZipFile(DOCX, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in media_map:
                data = media_map[info.filename]
            zout.writestr(info, data)
    tmp.unlink(missing_ok=True)
    print("Updated", DOCX)


if __name__ == "__main__":
    main()
