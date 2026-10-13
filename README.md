# 剪贴板链接打开 · clipboard-link-opener

> 复制任何 App / 网页的分享文案后，点开扩展即可从剪贴板中提取真实链接并一键打开对应网页。

一个零依赖、纯本地的 Manifest V3 Chrome / Edge 扩展。很多 App 点「分享 / 复制链接」出来的
并不是纯 URL，而是夹杂中文口令和推广语的文案（例如「7.99 复制打开抖音，看看【xxx】
https://v.douyin.com/xxxx/ 更多」），无法直接点击。本扩展会自动剥离口令、识别出其中的真实
链接（常见分享 / 短链优先排在最前），点一下就在新标签页打开。

## 功能特性

- **一键打开**：点击工具栏图标读取剪贴板，直接打开第一个链接。
- **智能提取**：从混杂中文标点和正文的分享文案中精准切出 URL，去重、补 `https://`、去尾部标点。
- **通用 + 优先**：任意 `http(s)://` 链接都能识别；命中已知分享 / 短链域名时排在最前并高亮。
- **多链接列表**：文案里有多个链接时全部列出（按域名标注），可分别点击或单独「打开」。
- **粘贴兜底**：浏览器因焦点/权限拒绝读取剪贴板时，自动降级为手动粘贴框，粘贴即解析。
- **零依赖、零联网**：不引入任何第三方库，不发送任何数据，不申请网络权限。

## 支持的分享 / 短链域名（优先识别裸域名）

内置常见平台前缀，命中时优先展示，其它任何站点仍按通用 URL 处理：

| 平台 | 域名 |
| --- | --- |
| 抖音 | `douyin.com` `iesdouyin.com` |
| B 站 | `bilibili.com` `b23.tv` |
| 小红书 | `xiaohongshu.com` `xhslink.com` |
| 微博 | `weibo.com` `weibo.cn` `t.cn` |
| X / Twitter | `twitter.com` `x.com` `t.co` |

需要新增平台，只改 `link-extract.js` 顶部的 `SHARE_ROOTS` 数组即可。

## 安装（加载已解压的扩展）

1. 下载或克隆本仓库到本地。
2. 打开 Chrome / Edge，访问 `chrome://extensions`（Edge 为 `edge://extensions`）。
3. 右上角开启「开发者模式」。
4. 点击「加载已解压的扩展程序」，选择**本仓库根目录**（即包含 `manifest.json` 的文件夹）。
5. 工具栏出现图标即可使用；建议固定到工具栏方便一键调用。

也可以直接使用 `tools/package.py` 生成的 `dist/clipboard-link-opener_v*.zip`（用于分享或上传商店）。

## 使用方法

1. 在目标 App 或网页中点「复制链接 / 分享」，让分享文案进入剪贴板。
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

`LINK_RE` 匹配任意 `http(s)://…` 链接，并对已知分享 / 短链域名额外支持「无协议头」的裸域名
（如直接出现 `v.douyin.com/…`）。中文标点、正文汉字及常见成对符号一律作为链接终止符，因此能
从口令文案中干净地取出 URL，去重后按是否命中分享域名排序。

## 权限说明

扩展仅申请 `clipboardRead` 一项权限，用途是在用户主动点开弹窗时读取剪贴板文本。
不申请任何网络、存储或历史权限；所有解析均在本地弹窗内完成，链接通过 `chrome.tabs.create`
在新标签页打开。

> 安全提示：通用版会识别剪贴板里的任意链接。跳转只在用户主动点击时发生，不会静默自动打开，
> 请自行判断链接来源是否可信。

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
clipboard-link-opener/
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
├── CHANGELOG.md
└── README.md
```

## 已知限制

- 部分浏览器在弹窗失焦时可能拒绝读取剪贴板，此时使用粘贴兜底框即可。
- 只提取 `http(s)://` 链接及 `SHARE_ROOTS` 里已知的裸域名；纯口令而无 URL 的文案无法识别。

## 许可

本仓库暂未添加开源许可证。若计划公开发布，建议在仓库根目录补充 `LICENSE` 文件（如 MIT）。
