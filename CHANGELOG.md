# 更新日志

本项目的所有重要变更都会记录在此文件中。版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-10-13

### 新增

- 抖音剪贴板链接打开：Manifest V3 扩展，读取剪贴板并从抖音分享文案中提取真实链接，一键在新标签页打开。
- 多链接列表与抖音域名优先排序；剪贴板被浏览器拦截时的手动粘贴兜底。
- 构建脚本：`tools/package.py`（引用校验 + 打包 store 可用 zip）、`tools/make-icons.py`（生成图标）。
- 仓库文档：`README.md`、本 `CHANGELOG.md`、`.gitignore`。

### 修复

- `popup.html` 缺失的 `<script>` 引用（`link-extract.js`、`popup.js`），此前会导致弹窗脚本不加载、功能不可用。
