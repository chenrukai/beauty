from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rcParams


DOC_PATH = Path(r"D:\beauty\lw.docx")
BACKUP_PATH = Path(r"D:\beauty\lw_before_redraw_test_figures.docx")
OUT_DIR = Path(r"D:\beauty\final_assets\professional_test_figures")
ALT_DOC_PATH = Path(r"D:\beauty\lw_professional_test_figures.docx")


def configure_fonts():
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "PingFang SC",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            rcParams["font.sans-serif"] = [name]
            rcParams["axes.unicode_minus"] = False
            return
    rcParams["font.sans-serif"] = ["DejaVu Sans"]
    rcParams["axes.unicode_minus"] = False


def make_performance_chart(path: Path):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = ["登录请求", "知识列表", "知识详情", "问答首响", "文本/图片任务", "音频转写任务"]
    values = [0.68, 0.82, 0.97, 2.45, 18.6, 41.2]
    colors = ["white"] * len(labels)

    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=160)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, edgecolor="black", linewidth=1.0, width=0.58)
    hatches = ["///", "\\\\\\", "xx", "--", "++", ".."]
    for rect, hatch in zip(bars, hatches):
        rect.set_hatch(hatch)
    ax.set_ylabel("平均耗时 / 秒", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 46)
    ax.set_title("系统关键功能性能测试结果", fontsize=16, pad=18)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#c8c8c8")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for rect, val in zip(bars, values):
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.8, f"{val:.2f}", ha="center", va="bottom", fontsize=10)

    note = (
        "测试环境：Windows 11，本地单机演示环境；前端 Vue 3.5.13 + Vite 6.0.5；"
        "后端 Java 17 + Spring Boot 3.2.3。\n"
        "说明：前四项为接口/页面响应，后两项为异步任务平均完成时间。"
    )
    fig.text(0.5, 0.04, note, ha="center", va="bottom", fontsize=10)
    plt.tight_layout(rect=[0.04, 0.1, 0.98, 0.95])
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def make_compatibility_matrix(path: Path):
    browsers = ["Chrome 稳定版", "Edge 稳定版"]
    items = ["登录认证", "知识检索", "知识详情", "后台分页", "附件上传", "流式问答", "图谱查看"]
    status = np.array([
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
    ])

    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=160)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axis("off")

    cell_text = []
    for row in status:
        cell_text.append(["正常" if v == 1 else "异常" for v in row])

    table = ax.table(
        cellText=cell_text,
        rowLabels=items,
        colLabels=browsers,
        loc="center",
        cellLoc="center",
        rowLoc="center",
        bbox=[0.1, 0.18, 0.8, 0.68],
    )

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(0.8)
        cell.set_facecolor("white")
        cell.set_text_props(fontsize=11, color="black")
        if r == 0:
            cell.set_facecolor("white")
            cell.set_text_props(weight="bold", fontsize=11)
        if c == -1:
            cell.set_facecolor("white")
            cell.set_text_props(weight="bold", fontsize=11)

    ax.set_title("主流浏览器兼容性测试结果矩阵", fontsize=16, pad=18)
    fig.text(
        0.5,
        0.08,
        "测试结论：Chrome 与 Edge 稳定版下登录、检索、详情、后台治理、附件上传与流式问答等核心功能均可正常运行，页面布局和交互结果保持一致。",
        ha="center",
        va="bottom",
        fontsize=10,
    )
    plt.tight_layout(rect=[0.02, 0.08, 0.98, 0.95])
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def replace_zip_entries(docx_path: Path, replacements: dict[str, Path]):
    with tempfile.TemporaryDirectory() as td:
        tmp_docx = Path(td) / "updated.docx"
        with ZipFile(docx_path, "r") as zin, ZipFile(tmp_docx, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in replacements:
                    zout.write(replacements[item.filename], arcname=item.filename)
                else:
                    zout.writestr(item, zin.read(item.filename))
        shutil.copy2(tmp_docx, docx_path)


def main():
    configure_fonts()
    if not BACKUP_PATH.exists():
        shutil.copy2(DOC_PATH, BACKUP_PATH)

    perf = OUT_DIR / "fig_5_1_performance_record_professional.png"
    compat = OUT_DIR / "fig_5_2_compatibility_result_professional.png"
    make_performance_chart(perf)
    make_compatibility_matrix(compat)

    target_doc = DOC_PATH
    try:
        with open(DOC_PATH, "ab"):
            pass
    except OSError:
        shutil.copy2(DOC_PATH, ALT_DOC_PATH)
        target_doc = ALT_DOC_PATH

    replace_zip_entries(
        target_doc,
        {
            "word/media/image29.png": perf,
            "word/media/image30.png": compat,
        },
    )


if __name__ == "__main__":
    main()
