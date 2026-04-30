from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(r"D:\beauty")
ASSET_DIR = ROOT / "论文图表素材"
OUTPUT_DIR = ASSET_DIR / "png_for_word"
TMP_DIR = ROOT / "tmp_png_export"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

TARGETS = [
    "fig_3_1_system_architecture.svg",
    "fig_3_2_er_diagram.svg",
    "fig_2_2_user_usecase.svg",
    "fig_2_3_admin_usecase.svg",
    "fig_4_1_detail_collaboration.svg",
    "fig_4_2_frontend_navigation.svg",
    "fig_4_3_knowledge_manage_flow.svg",
    "fig_4_4_file_processing_flow.svg",
    "fig_4_5_graph_query_flow.svg",
    "fig_4_6_qa_flow.svg",
]


def to_file_url(path: Path) -> str:
    return "file:///" + quote(str(path).replace("\\", "/"), safe="/:.")


def export_svg(svg_name: str) -> Path:
    svg_path = ASSET_DIR / svg_name
    png_path = OUTPUT_DIR / (svg_path.stem + ".png")
    tmp_png_path = TMP_DIR / (svg_path.stem + ".png")
    cmd = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        f"--screenshot={tmp_png_path}",
        "--window-size=1600,1200",
        to_file_url(svg_path),
    ]
    subprocess.run(cmd, check=True)
    png_path.write_bytes(tmp_png_path.read_bytes())
    return png_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    for svg_name in TARGETS:
        png_path = export_svg(svg_name)
        print(png_path)


if __name__ == "__main__":
    main()
