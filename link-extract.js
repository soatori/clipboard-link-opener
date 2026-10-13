// 从分享文案中提取真实链接：中文标点、正文汉字与常见成对符号一律作为链接终止符。
// 只提取带协议的 http(s) 链接（几乎所有 App 的「复制链接」都含协议头）；javascript:/data: 等
// 非 http 方案不会被匹配。SHARE_ROOTS 用于把常见分享 / 短链域名排在前面并高亮。

const SHARE_ROOTS = [
  'douyin.com', 'iesdouyin.com', // 抖音
  'bilibili.com', 'b23.tv', // B 站
  'xiaohongshu.com', 'xhslink.com', // 小红书
  'weibo.com', 'weibo.cn', 't.cn', // 微博
  'twitter.com', 'x.com', 't.co', // X / Twitter
];

const LINK_STOP = String.raw`\s\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef\u2000-\u206f"'<>\[\]{}`;

// 仅匹配 http(s)://…；遇到空白、中日韩字符、全角标点或成对符号即终止。
const LINK_RE = new RegExp('https?:\\/\\/[^' + LINK_STOP + ']+', 'gi');

function normalizeUrl(raw) {
  const url = raw.trim().replace(/["'<>[\]{}.,;:!?]+$/, '');
  try {
    return new URL(url).href;
  } catch {
    return null;
  }
}

const SHARE_SUFFIXES = SHARE_ROOTS.map((h) => h.toLowerCase());

function isShare(url) {
  const host = new URL(url).hostname.toLowerCase();
  return SHARE_SUFFIXES.some((s) => host === s || host.endsWith('.' + s));
}

function extractLinks(text) {
  if (!text) return [];
  const seen = new Set();
  const links = [];
  for (const match of text.match(LINK_RE) || []) {
    const url = normalizeUrl(match);
    if (!url || seen.has(url)) continue;
    seen.add(url);
    links.push({ url, host: new URL(url).hostname, share: isShare(url) });
  }
  return links.sort((a, b) => Number(b.share) - Number(a.share));
}
