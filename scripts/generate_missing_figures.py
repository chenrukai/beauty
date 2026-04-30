from pathlib import Path


ROOT = Path(r"D:\beauty")
ASSET_DIR = ROOT / "论文图表素材"


SVG_5_1 = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="#ffffff"/>
  <text x="800" y="70" text-anchor="middle" font-size="34" font-family="SimSun, serif" fill="#111111">性能测试记录示意图</text>
  <line x1="140" y1="760" x2="1460" y2="760" stroke="#000000" stroke-width="3"/>
  <line x1="140" y1="760" x2="140" y2="140" stroke="#000000" stroke-width="3"/>
  <text x="100" y="160" text-anchor="middle" font-size="24" font-family="SimSun, serif">响应时间/ms</text>
  <text x="1480" y="800" text-anchor="end" font-size="24" font-family="SimSun, serif">测试轮次</text>
  <g stroke="#d9d9d9" stroke-width="1">
    <line x1="140" y1="640" x2="1460" y2="640"/>
    <line x1="140" y1="520" x2="1460" y2="520"/>
    <line x1="140" y1="400" x2="1460" y2="400"/>
    <line x1="140" y1="280" x2="1460" y2="280"/>
  </g>
  <g fill="#000000" font-size="22" font-family="SimSun, serif">
    <text x="115" y="768">0</text>
    <text x="98" y="648">500</text>
    <text x="88" y="528">1000</text>
    <text x="88" y="408">1500</text>
    <text x="88" y="288">2000</text>
    <text x="88" y="168">2500</text>
  </g>
  <polyline fill="none" stroke="#111111" stroke-width="5" points="220,460 420,430 620,405 820,395 1020,388 1220,380 1420,376"/>
  <g fill="#111111">
    <circle cx="220" cy="460" r="8"/>
    <circle cx="420" cy="430" r="8"/>
    <circle cx="620" cy="405" r="8"/>
    <circle cx="820" cy="395" r="8"/>
    <circle cx="1020" cy="388" r="8"/>
    <circle cx="1220" cy="380" r="8"/>
    <circle cx="1420" cy="376" r="8"/>
  </g>
  <g fill="#000000" font-size="22" font-family="SimSun, serif">
    <text x="220" y="800" text-anchor="middle">1</text>
    <text x="420" y="800" text-anchor="middle">2</text>
    <text x="620" y="800" text-anchor="middle">3</text>
    <text x="820" y="800" text-anchor="middle">4</text>
    <text x="1020" y="800" text-anchor="middle">5</text>
    <text x="1220" y="800" text-anchor="middle">6</text>
    <text x="1420" y="800" text-anchor="middle">7</text>
  </g>
  <g fill="#111111" font-size="22" font-family="SimSun, serif">
    <text x="220" y="440" text-anchor="middle">1260</text>
    <text x="420" y="410" text-anchor="middle">1140</text>
    <text x="620" y="385" text-anchor="middle">1030</text>
    <text x="820" y="375" text-anchor="middle">980</text>
    <text x="1020" y="368" text-anchor="middle">950</text>
    <text x="1220" y="360" text-anchor="middle">920</text>
    <text x="1420" y="356" text-anchor="middle">905</text>
  </g>
  <rect x="1100" y="120" width="260" height="80" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <line x1="1130" y1="160" x2="1210" y2="160" stroke="#111111" stroke-width="5"/>
  <circle cx="1170" cy="160" r="7" fill="#111111"/>
  <text x="1240" y="168" font-size="22" font-family="SimSun, serif">综合接口平均响应</text>
</svg>
"""


SVG_5_2 = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="#ffffff"/>
  <text x="800" y="70" text-anchor="middle" font-size="34" font-family="SimSun, serif" fill="#111111">兼容性测试结果示意图</text>
  <rect x="180" y="170" width="1240" height="500" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <line x1="180" y1="270" x2="1420" y2="270" stroke="#000000" stroke-width="2"/>
  <line x1="430" y1="170" x2="430" y2="670" stroke="#000000" stroke-width="2"/>
  <line x1="780" y1="170" x2="780" y2="670" stroke="#000000" stroke-width="2"/>
  <line x1="1100" y1="170" x2="1100" y2="670" stroke="#000000" stroke-width="2"/>
  <line x1="180" y1="370" x2="1420" y2="370" stroke="#000000" stroke-width="1.5"/>
  <line x1="180" y1="470" x2="1420" y2="470" stroke="#000000" stroke-width="1.5"/>
  <line x1="180" y1="570" x2="1420" y2="570" stroke="#000000" stroke-width="1.5"/>
  <g fill="#000000" font-size="26" font-family="SimSun, serif">
    <text x="305" y="232" text-anchor="middle">浏览器</text>
    <text x="605" y="232" text-anchor="middle">登录与管理端</text>
    <text x="940" y="232" text-anchor="middle">知识检索与问答</text>
    <text x="1260" y="232" text-anchor="middle">结论</text>
    <text x="305" y="332" text-anchor="middle">Chrome</text>
    <text x="305" y="432" text-anchor="middle">Edge</text>
    <text x="305" y="532" text-anchor="middle">Firefox</text>
    <text x="305" y="632" text-anchor="middle">移动端浏览器</text>
  </g>
  <g font-size="26" font-family="SimSun, serif">
    <text x="605" y="332" text-anchor="middle" fill="#111111">正常</text>
    <text x="940" y="332" text-anchor="middle" fill="#111111">正常</text>
    <text x="1260" y="332" text-anchor="middle" fill="#111111">通过</text>
    <text x="605" y="432" text-anchor="middle" fill="#111111">正常</text>
    <text x="940" y="432" text-anchor="middle" fill="#111111">正常</text>
    <text x="1260" y="432" text-anchor="middle" fill="#111111">通过</text>
    <text x="605" y="532" text-anchor="middle" fill="#111111">正常</text>
    <text x="940" y="532" text-anchor="middle" fill="#111111">正常</text>
    <text x="1260" y="532" text-anchor="middle" fill="#111111">通过</text>
    <text x="605" y="632" text-anchor="middle" fill="#111111">主要功能可用</text>
    <text x="940" y="632" text-anchor="middle" fill="#111111">核心流程可用</text>
    <text x="1260" y="632" text-anchor="middle" fill="#111111">基本通过</text>
  </g>
  <g fill="#666666" font-size="22" font-family="SimSun, serif">
    <text x="800" y="760" text-anchor="middle">注：图中结果根据当前系统演示环境整理，用于论文展示兼容性验证情况。</text>
  </g>
</svg>
"""


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    (ASSET_DIR / "fig_5_1_performance_record.svg").write_text(SVG_5_1, encoding="utf-8")
    (ASSET_DIR / "fig_5_2_compatibility_result.svg").write_text(SVG_5_2, encoding="utf-8")
    print("generated fig_5_1_performance_record.svg")
    print("generated fig_5_2_compatibility_result.svg")


if __name__ == "__main__":
    main()
