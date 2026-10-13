const openBtn = document.getElementById('openLink');
const statusEl = document.getElementById('status');
const linksEl = document.getElementById('links');
const fallbackEl = document.getElementById('fallback');
const pasteEl = document.getElementById('paste');
const targetEl = document.getElementById('target');
const targetHostEl = document.getElementById('targetHost');
const targetUrlEl = document.getElementById('targetUrl');

const IDLE_TEXT = '点击后读取剪贴板，自动提取分享文案里的链接并打开网页';

async function readClipboard() {
  try {
    return await navigator.clipboard.readText();
  } catch {
    return null;
  }
}

function showFallback() {
  fallbackEl.classList.remove('hidden');
}

// 读取剪贴板；失败时（焦点丢失 / 站点权限拦截）按需退化为手动粘贴框。
async function currentText(revealFallback) {
  const text = await readClipboard();
  if (text !== null) return text;
  if (revealFallback) showFallback();
  return pasteEl.value;
}

function setStatus(message, kind = '') {
  statusEl.textContent = message;
  statusEl.className = kind ? `status ${kind}` : 'status';
}

function openUrl(link) {
  chrome.tabs.create({ url: link.url });
  setStatus(`已打开 ${link.url}`, 'ok');
}

// 醒目显示「一键打开」将指向的目标站点与完整链接。
function renderTarget(links) {
  if (!links.length) {
    targetEl.classList.add('hidden');
    return;
  }
  const first = links[0];
  targetHostEl.textContent = first.host;
  targetUrlEl.textContent = first.url;
  targetEl.classList.remove('hidden');
}

function renderLinks(links) {
  linksEl.textContent = '';
  for (const link of links) {
    const li = document.createElement('li');

    const chip = document.createElement('span');
    chip.className = link.share ? 'chip' : 'chip other';
    chip.textContent = link.host;

    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'row';
    row.textContent = link.url;
    row.addEventListener('click', () => openUrl(link));

    const tail = document.createElement('button');
    tail.type = 'button';
    tail.className = 'row-open';
    tail.textContent = '打开';
    tail.addEventListener('click', () => openUrl(link));

    li.append(chip, row, tail);
    linksEl.append(li);
  }
  renderTarget(links);
}

function refresh() {
  const links = extractLinks(pasteEl.value);
  renderLinks(links);
  setStatus(links.length ? `找到 ${links.length} 个链接` : '粘贴的文案里没有链接', links.length ? '' : 'warn');
  return links;
}

openBtn.addEventListener('click', async () => {
  const links = extractLinks(await currentText(true));
  renderLinks(links);
  if (!links.length) {
    setStatus('剪贴板为空或没有链接，请先在 App / 网页里点“复制链接”或“分享”', 'warn');
    return;
  }
  openUrl(links[0]);
});

pasteEl.addEventListener('input', refresh);

pasteEl.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter') return;
  event.preventDefault();
  const links = refresh();
  if (links.length) openUrl(links[0]);
});

(async function init() {
  const links = extractLinks(await currentText(false));
  renderLinks(links);
  if (!links.length) {
    setStatus(IDLE_TEXT);
    return;
  }
  setStatus(links.length > 1 ? `找到 ${links.length} 个链接，“打开链接”进入上方指向的站点` : '已识别剪贴板链接，点“打开链接”跳转');
})();
