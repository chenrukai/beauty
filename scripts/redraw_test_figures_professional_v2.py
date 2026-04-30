from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.patches import Rectangle


ROOT = Path(r"D:\beauty")
DOCX_PATH = ROOT / "lw.docx"
FALLBACK_DOCX_PATH = ROOT / "lw_professional_test_figures.docx"
ASSET_DIR = ROOT / "final_assets" / "professional_test_figures"
PERF_PNG = ASSET_DIR / "fig_5_1_performance_record_professional.png"
COMPAT_PNG = ASSET_DIR / "fig_5_2_compatibility_result_professional.png"

PERF_MEDIA = "word/media/image29.png"
COMPAT_MEDIA = "word/media/image30.png"


def configure_chinese_font() -> None:
    preferred = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "PingFang SC",
    ]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in installed:
            rcParams["font.sans-serif"] = [name]
            break
    rcParams["axes.unicode_minus"] = False


def ensure_asset_dir() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def draw_performance_chart(output_path: Path) -> None:
    labels = ["登录请求", "知识列表", "知识详情", "问答首响", "文本/图片任务"]
    values = [0.72, 0.88, 0.96, 2.64, 18.3]
    limit = 20

    fig, ax = plt.subplots(figsize=(11.5, 6.8), facecolor="white")
    ax.set_facecolor("white")

    y_pos = list(range(len(labels)))
    bars = ax.barh(
        y_pos,
        values,
        height=0.58,
        color="white",
        edgecolor="black",
        linewidth=1.4,
        hatch="///",
    )

    for idx, (bar, value) in enumerate(zip(bars, values)):
        text = f"{value:.2f} s" if idx < 4 else f"{value:.1f} s"
        ax.text(
            min(value + 0.4, limit - 0.8),
            bar.get_y() + bar.get_height() / 2,
            text,
            va="center",
            ha="left",
            fontsize=11,
            color="black",
        )

    ax.set_yticks(y_pos, labels, fontsize=12)
    ax.set_xlim(0, limit)
    ax.set_xlabel("平均响应时间 / 处理耗时（秒）", fontsize=12)
    ax.set_title("系统性能测试结果统计图", fontsize=15, pad=16)
    ax.grid(axis="x", color="black", alpha=0.12, linestyle="-", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()

    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color("black")

    note = (
        "说明：登录、列表与详情请求均控制在 1 s 左右；智能问答首屏返回约 2~3 s；"
        "文本或图片附件处理任务平均完成时间约 18 s。"
    )
    fig.text(0.5, 0.02, note, ha="center", fontsize=10.5, color="black")
    plt.tight_layout(rect=[0.04, 0.06, 0.98, 0.94])
    fig.savefig(output_path, dpi=220, facecolor="white", edgecolor="white")
    plt.close(fig)


def draw_compatibility_chart(output_path: Path) -> None:
    columns = ["测试项", "Chrome 134", "Edge 134", "结果说明"]
    rows = [
        ("登录与鉴权", "通过", "通过", "登录、退出与权限分流正常"),
        ("知识检索", "通过", "通过", "关键词检索、分页与详情跳转正常"),
        ("文件上传", "通过", "通过", "文本、图片附件上传与回显正常"),
        ("智能问答", "通过", "通过", "流式回答、追问与会话记录正常"),
        ("图谱查询", "通过", "通过", "图谱检索与关系展示正常"),
        ("后台管理", "通过", "通过", "知识、分类、公告与任务管理正常"),
    ]

    fig, ax = plt.subplots(figsize=(12.0, 6.6), facecolor="white")
    ax.set_facecolor("white")
    ax.axis("off")

    left = 0.05
    bottom = 0.08
    total_width = 0.90
    total_height = 0.80
    col_widths = [0.24, 0.16, 0.16, 0.44]
    row_count = len(rows) + 1
    row_h = total_height / row_count

    x_positions = [left]
    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + total_width * w)

    def draw_cell(x: float, y: float, w: float, h: float, text: str, bold: bool = False) -> None:
        rect = Rectangle((x, y), w, h, facecolor="white", edgecolor="black", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=11 if not bold else 11.5,
            fontweight="bold" if bold else "normal",
            color="black",
            wrap=True,
        )

    y = bottom + total_height - row_h
    for i, col in enumerate(columns):
        draw_cell(x_positions[i], y, total_width * col_widths[i], row_h, col, bold=True)

    for row_index, row in enumerate(rows, start=1):
        y = bottom + total_height - row_h * (row_index + 1)
        for col_index, cell in enumerate(row):
            draw_cell(x_positions[col_index], y, total_width * col_widths[col_index], row_h, cell)

    ax.text(0.5, 0.94, "主流浏览器兼容性测试结果矩阵", ha="center", va="center", fontsize=15, color="black")
    ax.text(
        0.5,
        0.03,
        "说明：测试环境为 Windows 11，本地部署前后端与中间件服务，分别在 Chrome 与 Edge 稳定版下完成功能验证。",
        ha="center",
        va="center",
        fontsize=10.5,
        color="black",
    )

    fig.savefig(output_path, dpi=220, facecolor="white", edgecolor="white")
    plt.close(fig)


def replace_media(docx_path: Path, replacements: dict[str, Path]) -> None:
    tmp_path = docx_path.with_name(docx_path.stem + "_tmp_replace.docx")
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in replacements:
                zout.write(replacements[item.filename], item.filename)
            else:
                zout.writestr(item, zin.read(item.filename))
    shutil.move(tmp_path, docx_path)


def update_docx() -> Path:
    target = DOCX_PATH
    try:
        replace_media(
            target,
            {
                PERF_MEDIA: PERF_PNG,
                COMPAT_MEDIA: COMPAT_PNG,
            },
        )
        return target
    except PermissionError:
        shutil.copy2(DOCX_PATH, FALLBACK_DOCX_PATH)
        replace_media(
            FALLBACK_DOCX_PATH,
            {
                PERF_MEDIA: PERF_PNG,
                COMPAT_MEDIA: COMPAT_PNG,
            },
        )
        return FALLBACK_DOCX_PATH


def main() -> None:
    configure_chinese_font()
    ensure_asset_dir()
    draw_performance_chart(PERF_PNG)
    draw_compatibility_chart(COMPAT_PNG)
    updated = update_docx()
    print(updated)


if __name__ == "__main__":
    main()
