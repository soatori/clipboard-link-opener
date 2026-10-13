"""校验并打包 Chrome 扩展：检查 manifest / popup.html 引用的文件齐全，输出可上传/分享的 zip。

用法:  python tools/package.py
输出:  dist/douyin-clipboard-link_v<version>.zip（manifest.json 位于压缩包根目录）

仓库布局：扩展文件直接放在仓库根目录，本脚本位于 tools/。打包时只收录扩展所需文件，
排除 tools/、dist/、README、.gitignore 等仓库文件。
"""

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 仓库根目录 = 扩展目录
DIST_DIR = ROOT / "dist"

# 收录进压缩包的内容：这些固定的顶层文件 + icons 目录下所有文件。
INCLUDE_FILES = ["manifest.json", "popup.html", "popup.css", "popup.js", "link-extract.js"]
INCLUDE_DIRS = ["icons"]

ASSET_RE = re.compile(r"\.(?:js|css|html|png|svg|json)$")


def manifest_file_refs(node):
    if isinstance(node, str):
        return [node] if ASSET_RE.search(node) else []
    if isinstance(node, dict):
        return [p for v in node.values() for p in manifest_file_refs(v)]
    if isinstance(node, list):
        return [p for v in node for p in manifest_file_refs(v)]
    return []


def popup_assets(html):
    return [m for m in re.findall(r'(?:src|href)="([^":]+)"', html) if ASSET_RE.search(m)]


def collect():
    files = []
    for rel in INCLUDE_FILES:
        files.append(rel)
    for d in INCLUDE_DIRS:
        for f in sorted((ROOT / d).rglob("*")):
            if f.is_file():
                files.append(f.relative_to(ROOT).as_posix())
    return files


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    problems = []

    for rel in manifest_file_refs(manifest):
        if not (ROOT / rel).is_file():
            problems.append(f"manifest 引用缺失: {rel}")

    popup = manifest.get("action", {}).get("default_popup")
    if popup and (ROOT / popup).is_file():
        html = (ROOT / popup).read_text(encoding="utf-8")
        for rel in popup_assets(html):
            if not (ROOT / rel).is_file():
                problems.append(f"{popup} 引用缺失: {rel}")
    elif popup:
        problems.append(f"popup 文件缺失: {popup}")

    allowed = {"clipboardRead", "clipboardWrite", "storage", "tabs"}
    for perm in manifest.get("permissions", []):
        if perm not in allowed:
            problems.append(f"未预期的权限，需向用户说明: {perm}")

    for rel in collect():
        if not (ROOT / rel).is_file():
            problems.append(f"待打包文件缺失: {rel}")

    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"{ROOT.name}_v{manifest['version']}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in collect():
            zf.write(ROOT / rel, rel)

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    assert "manifest.json" in names, "manifest.json 必须在压缩包根目录"
    print(f"OK  {zip_path.relative_to(ROOT).as_posix()}  ({len(names)} 个文件)")
    for name in names:
        print("   ", name)


if __name__ == "__main__":
    main()
