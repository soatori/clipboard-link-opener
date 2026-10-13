// 从抖音分享文案中提取真实链接：中文标点和正文汉字一律作为链接终止符。
const DOUYIN_HOSTS = ['v.douyin.com', 'www.douyin.com', 'douyin.com', 'www.iesdouyin.com', 'iesdouyin.com'];

const LINK_STOP = String.raw`\s\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef\u2000-\u206f"'<>\[\]{}`;

const LINK_RE = new RegExp(
  'https?:\\/\\/[^' + LINK_STOP + ']+' +
    '|(?:' + DOUYIN_HOSTS.map((h) => h.replace(/\./g, '\\.')).join('|') + ')\\/[^' + LINK_STOP + ']*',
  'g'
);

function normalizeUrl(raw) {
  let url = raw.trim().replace(/["'<>[\]{}.,;:!?]+$/, '');
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  try {
    return new URL(url).href;
  } catch {
    return null;
  }
}

function isDouyin(url) {
  const host = new URL(url).hostname.toLowerCase();
  return DOUYIN_HOSTS.includes(host) || host.endsWith('.douyin.com');
}

function extractLinks(text) {
  if (!text) return [];
  const seen = new Set();
  const links = [];
  for (const match of text.match(LINK_RE) || []) {
    const url = normalizeUrl(match);
    if (!url || seen.has(url)) continue;
    seen.add(url);
    links.push({ url, host: new URL(url).hostname, douyin: isDouyin(url) });
  }
  return links.sort((a, b) => Number(b.douyin) - Number(a.douyin));
}
