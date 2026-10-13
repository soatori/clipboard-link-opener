# 抖音剪贴板链接打开 · douyin-clipboard-link

> 复制抖音分享文案后，点开扩展即可从剪贴板中提取真实链接并一键打开对应网页。

一个零依赖、纯本地的 Manifest V3 Chrome / Edge 扩展。在抖音里点「复制链接」，分享文案里
通常夹杂着「7.99 复制打开抖音…」之类的中文口令，无法直接点击。本扩展会自动剥离口令、
识别出其中的真实链接（优先抖音域名），点一下就在新标签页打开。

## 功能特性

- **一键打开**：点击工具栏图标读取剪贴板，直接打开第一个链接。
- **智能提取**：从混杂中文标点和正文的分享文案中精准切出 URL，去重后抖音链接排在最前。
- **多链接列表**：文案里有多个链接时全部列出，可分别点击或单独「打开」。
- **粘贴兜底**：浏览器因焦点/权限拒绝读取剪贴板时，自动降级为手动粘贴框，粘贴即解析。
- **零依赖、零联网**：不引入任何第三方库，不发送任何数据，不申请网络权限。

## 安装（加载已解压的扩展）

1. 下载或克隆本仓库到本地。
2. 打开 Chrome / Edge，访问 `chrome://extensions`（Edge 为 `edge://extensions`）。
3. 右上角开启「开发者模式」。
4. 点击「加载已解压的扩展程序」，选择**本仓库根目录**（即包含 `manifest.json` 的文件夹）。
5. 工具栏出现图标即可使用；建议固定到工具栏方便一键调用。

也可以直接使用 `tools/package.py` 生成的 `dist/douyin-clipboard-link_v*.zip`（用于分享或上传商店）。

## 使用方法

1. 在抖音 App 或网页中点「复制链接」，让分享文案进入剪贴板。
2. 点开浏览器工具栏的扩展图标。
3. 弹窗会自动读取剪贴板并显示识别到的链接：
   - 单个链接 → 点「打开链接」直接跳转。
   - 多个链接 → 在列表中点你想打开的那一条，或点行尾「打开」。
4. 若弹窗提示剪贴板被拦截，在出现的粘贴框里 `Ctrl + V` 粘贴文案，回车或点按钮即可。

## 工作原理

| 文件 | 作用 |
| --- | --- |
| `manifest.json` | MV3 清单，声明 `clipboardRead` 权限与弹窗入口 |
| `popup.html` / `popup.css` | 弹窗界面与样式 |
| `popup.js` | 读取剪贴板、渲染链接列表、打开标签页、粘贴兜底交互 |
| `link-extract.js` | 从分享文案中提取并规范化链接的核心逻辑（`extractLinks`） |
| `icons/` | 16 / 32 / 48 / 128 图标 |

链接提取把中文标点、汉字及常见成对符号一律视作链接终止符，因此能从
「…7.99 复制打开抖音，看看【xxx】https://v.douyin.com/xxxx/ 更多」这类口令里干净地取出
`https://v.douyin.com/xxxx/`，并对结果去重、按抖音域名优先排序。

## 权限说明

扩展仅申请 `clipboardRead` 一项权限，用途是在用户主动点开弹窗时读取剪贴板文本。
不申请任何网络、存储或历史权限；所有解析均在本地弹窗内完成，链接通过 `chrome.tabs.create`
在新标签页打开。

## 开发与打包

工具脚本在 `tools/` 目录下，仓库根目录即扩展本体。

```bash
# 校验 manifest/popup 引用是否齐全，并打包到 dist/（manifest.json 位于压缩包根目录）
python tools/package.py

# 重新生成图标（仅改图标时需要，会安装 Pillow）
pip install -r tools/requirements.txt
python tools/make-icons.py
```

`package.py` 会在打包前检查：manifest 与 popup.html 引用的文件是否存在、权限是否在白名单内、
待打包文件是否齐全，任一不通过即报错退出。

## 目录结构

```
douyin-clipboard-link/
├── manifest.json
├── popup.html
├── popup.css
├── popup.js
├── link-extract.js
├── icons/
│   ├── icon-16.png
│   ├── icon-32.png
│   ├── icon-48.png
│   └── icon-128.png
├── tools/
│   ├── package.py        # 校验 + 打包
│   ├── make-icons.py     # 生成图标
│   └── requirements.txt  # 仅图标工具依赖 (Pillow)
├── dist/                 # 打包产物（已被 .gitignore 忽略）
├── .gitignore
└── README.md
```

## 已知限制

- 部分浏览器在弹窗失焦时可能拒绝读取剪贴板，此时使用粘贴兜底框即可。
- 只提取 `http(s)://` 及常见抖音域名链接；纯口令而无 URL 的文案无法识别。

## 许可

本仓库暂未添加开源许可证。若计划公开发布，建议在仓库根目录补充 `LICENSE` 文件（如 MIT）。
