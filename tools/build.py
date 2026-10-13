"""按目标浏览器构建发布包：从同一份源码生成 普通/chrome/edge/firefox 四种 zip。

用法:
    python tools/build.py                 # 构建全部四种
    python tools/build.py firefox chrome  # 只构建指定目标

输出: dist/clipboard-link-opener-<target>_v<version>.zip   (manifest.json 位于压缩包根目录)

差异说明:
    - generic / chrome / edge : 纯 Chromium Manifest V3，内容一致，仅命名区分投放目标。
    - firefox : 额外注入 browser_specific_settings.gecko（AMO 上传/签名要求 id 与 strict_min_version）。

文件清单与引用校验复用 package.py，作为单一来源。
"""

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package  # noqa: E402  复用 ROOT / collect() / validate()

DIST = package.ROOT / "dist"

# Firefox 扩展 id（反向域名风格，仅作标识；发布到 AMO 前需在 AMO 上注册同名）
GECKO = {"gecko": {"id": "clipboard-link-opener@soatori.github.io", "strict_min_version": "109.0"}}

TARGETS = ["generic", "chrome", "edge", "firefox"]


def version():
    return json.loads((package.ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]


def patch_manifest(path, target):
    m = json.loads(path.read_text(encoding="utf-8"))
    if target == "firefox":
        m["browser_specific_settings"] = GECKO
    path.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(target):
    # 在系统临时目录里组装（不触碰用户目录），完成后自动清理
    tmp = Path(tempfile.mkdtemp(prefix=f"clo_{target}_"))
    try:
        for rel in package.collect():  # 单一来源：与 package.py 打包同一批文件
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(package.ROOT / rel, dest)
        patch_manifest(tmp / "manifest.json", target)

        zip_path = DIST / f"{package.ROOT.name}-{target}_v{version()}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(tmp.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(tmp).as_posix())
        assert "manifest.json" in zipfile.ZipFile(zip_path).namelist()
        return zip_path
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    targets = sys.argv[1:] or TARGETS
    bad = [t for t in targets if t not in TARGETS]
    if bad:
        print(f"未知目标: {bad}，可选: {TARGETS}", file=sys.stderr)
        sys.exit(1)

    problems = package.validate()  # 打包前统一校验引用/权限，缺文件即中止
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)

    DIST.mkdir(exist_ok=True)
    for t in targets:
        print("OK ", build(t).name)


if __name__ == "__main__":
    main()
