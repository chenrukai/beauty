from __future__ import annotations

from pathlib import Path
import shutil

from vsdx import VisioFile


SOURCE = Path(r"D:\beauty\final_assets\thesis_copy_fix\thesis_selected_figures.vsdx")
OUT_DIR = SOURCE.parent


def safe_name(page_name: str) -> str:
    return (
        page_name.replace("_", "-")
        .replace(" ", "")
        .replace("/", "-")
        .replace("\\", "-")
    )


def main() -> None:
    with VisioFile(str(SOURCE)) as vf:
        page_names = vf.get_page_names()

    for keep_name in page_names:
        target = OUT_DIR / f"{safe_name(keep_name)}.vsdx"
        shutil.copy2(SOURCE, target)
        with VisioFile(str(target)) as vf:
            names = vf.get_page_names()
            for idx in range(len(names) - 1, -1, -1):
                if names[idx] != keep_name:
                    vf.remove_page_by_index(idx)
            vf.save_vsdx(str(target))
        print(target)


if __name__ == "__main__":
    main()
