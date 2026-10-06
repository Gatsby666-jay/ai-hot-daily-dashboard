# -*- coding: utf-8 -*-
import json, html
from datetime import datetime, timedelta

SRC = "dailies_latest.json"
OUT = "ai_daily_dashboard.html"

WEEK = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]

def bj(dtstr):
    """Parse UTC ISO string, shift to Asia/Shanghai (+8), return datetime."""
    if not dtstr:
        return None
    s = dtstr.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s) + timedelta(hours=8)
    return dt

def fmt_date(dt):
    return f"{dt.year}年{dt.month}月{dt.day}日 {WEEK[dt.weekday()]}"

def fmt_monthday(dt):
    return f"{dt.month}月{dt.day}日"

def fmt_datetime(dt):
    return f"{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}时"

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

report = data["report"]
date = report["date"]
generated_at = report.get("generatedAt")
window_start = report.get("windowStart")
window_end = report.get("windowEnd")
attribution = report.get("attribution", {}) or {}
source_name = attribution.get("name", "AIHOT")
source_url = attribution.get("url", "https://aihot.news/daily/" + date)
lead = report.get("lead") or {}
lead_title = lead.get("title", "")

# Fixed five sections (label is the match key from the API)
FIXED = [
    ("models",   "模型发布/更新"),
    ("products", "产品发布/更新"),
    ("industry", "行业动态"),
    ("paper",    "论文研究"),
    ("tip",      "技巧与观点"),
]

api_sections = {s["label"]: s.get("items", []) for s in report.get("sections", [])}

MAX_SUMMARY = 60

def truncate(s):
    if not s:
        return ""
    s = s.strip()
    if len(s) <= MAX_SUMMARY:
        return s
    return s[:MAX_SUMMARY - 1] + "…"

sections_out = []
for key, label in FIXED:
    items = api_sections.get(label, [])
    out_items = []
    for it in items:
        title = it.get("title", "")
        summary = truncate(it.get("summary", ""))
        source_name_i = (it.get("source") or {}).get("name", "")
        links = it.get("links", {}) or {}
        aihot = links.get("aihot", "")
        original = links.get("original", "")
        is_lead = (title == lead_title)
        out_items.append({
            "title": title,
            "summary": summary,
            "source": source_name_i,
            "aihot": aihot,
            "original": original,
            "lead": is_lead,
        })
    sections_out.append({"key": key, "label": label, "items": out_items})

total = sum(len(s["items"]) for s in sections_out)

# Pre-convert all timestamps to Beijing human-readable strings (no ISO in output)
date_dt = bj(date + "T00:00:00Z")
gen_dt = bj(generated_at)
ws_dt = bj(window_start)
we_dt = bj(window_end)

payload = {
    "dateHuman": fmt_date(date_dt),
    "dateShort": fmt_monthday(date_dt),
    "windowHuman": f"{fmt_monthday(ws_dt)} — {fmt_monthday(we_dt)}",
    "generatedHuman": fmt_datetime(gen_dt) if gen_dt else "",
    "sourceName": source_name,
    "sourceUrl": source_url,
    "leadTitle": lead_title,
    "leadParagraph": lead.get("leadParagraph", ""),
    "total": total,
    "sections": sections_out,
}

# Escape the JSON for safe embedding inside <script>
json_str = json.dumps(payload, ensure_ascii=False)
json_str = json_str.replace("</", "<\\/")

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 晨报仪表盘 · __DATE__</title>
<style>
  :root{
    --bg:#0b0f17; --bg2:#111827; --card:#161e2e; --card2:#1b2538;
    --line:#243049; --txt:#e8edf6; --sub:#9fb0c9; --muted:#6b7a93;
    --accent:#5b8cff; --accent2:#7c5cff; --hot:#ff5b7a; --chip:#22304a;
    --shadow:0 10px 30px rgba(0,0,0,.35);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    background:radial-gradient(1200px 600px at 80% -10%,#1a2540 0%,transparent 60%),
               radial-gradient(900px 500px at -10% 0%,#241a40 0%,transparent 55%),
               var(--bg);
    color:var(--txt); line-height:1.6; padding:0 0 60px;
  }
  .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
  /* HERO */
  .hero{
    position:relative;overflow:hidden;
    background:linear-gradient(135deg,rgba(91,140,255,.16),rgba(124,92,255,.12));
    border:1px solid var(--line); border-radius:20px;
    padding:34px 30px 26px; margin:26px 0 22px; box-shadow:var(--shadow);
  }
  .hero::after{content:"";position:absolute;inset:0;background:
    radial-gradient(600px 200px at 90% -40%,rgba(255,91,122,.18),transparent 60%);pointer-events:none}
  .kicker{display:flex;align-items:center;gap:10px;flex-wrap:wrap;color:var(--sub);font-size:13px;letter-spacing:.04em}
  .kicker .tag{background:var(--chip);color:#cdd9ee;padding:4px 10px;border-radius:999px;border:1px solid var(--line)}
  .kicker a{color:var(--accent);text-decoration:none}
  .kicker a:hover{text-decoration:underline}
  .hero h1{font-size:clamp(26px,4vw,40px);margin:14px 0 6px;font-weight:800;letter-spacing:.5px}
  .hero .sub{color:var(--sub);font-size:15px}
  .stats{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}
  .stat{background:rgba(13,19,31,.55);border:1px solid var(--line);border-radius:14px;
    padding:12px 16px;min-width:96px;backdrop-filter:blur(6px)}
  .stat .num{font-size:26px;font-weight:800;color:#fff}
  .stat .lbl{font-size:12px;color:var(--muted);margin-top:2px}
  .stat.total .num{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
  /* NAV */
  .nav{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 26px}
  .nav a{text-decoration:none;color:var(--txt);background:var(--card);border:1px solid var(--line);
    padding:9px 15px;border-radius:999px;font-size:14px;display:flex;align-items:center;gap:8px;transition:.2s}
  .nav a:hover{border-color:var(--accent);transform:translateY(-1px)}
  .nav a .c{background:var(--chip);color:#bcd0f0;border-radius:999px;font-size:12px;padding:1px 9px;font-weight:700}
  .nav a.zero{opacity:.5}
  /* SECTION */
  section.block{margin:30px 0}
  .sec-head{display:flex;align-items:baseline;gap:12px;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
  .sec-head h2{font-size:21px;font-weight:800}
  .sec-head .cnt{color:var(--muted);font-size:14px}
  .sec-head .bar{width:4px;height:22px;border-radius:3px;background:linear-gradient(var(--accent),var(--accent2));align-self:center}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px}
  .card{position:relative;background:linear-gradient(180deg,var(--card),var(--card2));
    border:1px solid var(--line);border-radius:16px;padding:18px 18px 16px;display:flex;flex-direction:column;gap:10px;
    transition:.2s;overflow:hidden}
  .card:hover{border-color:var(--accent);transform:translateY(-3px);box-shadow:var(--shadow)}
  .card.lead{border-color:rgba(255,91,122,.55);background:linear-gradient(180deg,#231826,#1c1626)}
  .card .top{display:flex;align-items:center;gap:10px}
  .num{font-size:13px;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));
    width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;flex:0 0 auto}
  .badge{font-size:11px;font-weight:700;color:#fff;background:var(--hot);padding:3px 9px;border-radius:999px}
  .chip{margin-left:auto;font-size:12px;color:#cdd9ee;background:var(--chip);border:1px solid var(--line);
    padding:3px 10px;border-radius:999px;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .card h3{font-size:16.5px;line-height:1.4;font-weight:700}
  .card h3 a{color:var(--txt);text-decoration:none}
  .card h3 a:hover{color:var(--accent)}
  .card .summary{font-size:14px;color:var(--sub);flex:1}
  .card .meta{display:flex;align-items:center;gap:12px;font-size:13px;margin-top:2px}
  .src-link{color:var(--accent);text-decoration:none;font-weight:600}
  .src-link:hover{text-decoration:underline}
  .date-tag{color:var(--muted);font-size:12px}
  .empty{color:var(--muted);background:var(--card);border:1px dashed var(--line);border-radius:14px;
    padding:20px;text-align:center;font-size:14px;grid-column:1/-1}
  footer{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13px;
    display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center}
  footer a{color:var(--accent);text-decoration:none}
  footer a:hover{text-decoration:underline}
  @media(max-width:560px){.hero{padding:24px 18px}.stats{gap:8px}.stat{min-width:80px;padding:10px 12px}}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="kicker">
      <span class="tag">AI 晨报 · AI HOT</span>
      <span id="k-date"></span>
      <a id="k-src" href="#" target="_blank" rel="noopener noreferrer">数据来源 ↗</a>
    </div>
    <h1 id="h-title"></h1>
    <div class="sub" id="h-sub"></div>
    <div class="stats" id="stats"></div>
  </header>

  <nav class="nav" id="nav"></nav>

  <main id="main"></main>

  <footer id="footer"></footer>
</div>

<script>
const DATA = __JSON__;
const esc=s=>{const d=document.createElement('div');d.textContent=s;return d.innerHTML;};

// HERO
document.getElementById('k-date').textContent = "日报日期 " + DATA.dateHuman.replace(/星期/,'周');
document.getElementById('k-src').href = DATA.sourceUrl;
document.getElementById('h-title').textContent = DATA.dateHuman.replace(/星期/,'周');
document.getElementById('h-sub').textContent =
  "日报窗口 " + DATA.windowHuman + " · 生成于 " + DATA.generatedHuman;

const statsEl=document.getElementById('stats');
const totalStat=document.createElement('div');
totalStat.className='stat total';
totalStat.innerHTML='<div class="num">'+DATA.total+'</div><div class="lbl">总条数</div>';
statsEl.appendChild(totalStat);
DATA.sections.forEach(s=>{
  const el=document.createElement('div');
  el.className='stat';
  el.innerHTML='<div class="num">'+s.items.length+'</div><div class="lbl">'+esc(s.label)+'</div>';
  statsEl.appendChild(el);
});

// NAV
const navEl=document.getElementById('nav');
DATA.sections.forEach(s=>{
  const a=document.createElement('a');
  a.href='#sec-'+s.key;
  if(s.items.length===0) a.className='zero';
  a.innerHTML=esc(s.label)+' <span class="c">'+s.items.length+'</span>';
  navEl.appendChild(a);
});

// MAIN
const mainEl=document.getElementById('main');
let counter=0;
DATA.sections.forEach(s=>{
  const sec=document.createElement('section');
  sec.className='block';
  sec.id='sec-'+s.key;
  const head=document.createElement('div');
  head.className='sec-head';
  head.innerHTML='<span class="bar"></span><h2>'+esc(s.label)+'</h2><span class="cnt">'+s.items.length+' 条</span>';
  sec.appendChild(head);
  const grid=document.createElement('div');
  grid.className='grid';
  if(s.items.length===0){
    const e=document.createElement('div');
    e.className='empty';
    e.textContent='今日日报未收录「'+s.label+'」类内容。';
    grid.appendChild(e);
  } else {
    s.items.forEach(it=>{
      counter++;
      const card=document.createElement('article');
      card.className='card'+(it.lead?' lead':'');
      const badge=it.lead?'<span class="badge">今日头条</span>':'';
      const srcChip=it.source?'<span class="chip" title="'+esc(it.source)+'">'+esc(it.source)+'</span>':'';
      // original link: prefer original, fall back to aihot
      const origUrl = it.original || it.aihot;
      const origLabel = it.original ? '阅读原文 ↗' : '查看详情 ↗';
      const titleLink = it.aihot || it.original;
      card.innerHTML=
        '<div class="top"><span class="num">'+counter+'</span>'+badge+srcChip+'</div>'+
        '<h3><a href="'+esc(titleLink)+'" target="_blank" rel="noopener noreferrer">'+esc(it.title)+'</a></h3>'+
        '<div class="summary">'+esc(it.summary)+'</div>'+
        '<div class="meta">'+
          '<a class="src-link" href="'+esc(origUrl)+'" target="_blank" rel="noopener noreferrer">'+origLabel+'</a>'+
          '<span class="date-tag">'+DATA.dateShort+'</span>'+
        '</div>';
      grid.appendChild(card);
    });
  }
  sec.appendChild(grid);
  mainEl.appendChild(sec);
});

// FOOTER
document.getElementById('footer').innerHTML=
  '总条数 <b style="color:#cdd9ee">'+DATA.total+'</b> · '+
  '数据来源 <a href="'+esc(DATA.sourceUrl)+'" target="_blank" rel="noopener noreferrer">'+esc(DATA.sourceName)+'</a> '+
  '('+esc(DATA.sourceUrl)+') · 日报日期 '+
  DATA.dateHuman.replace(/星期/,'周')+
  ' · 由 AI HOT 公开 API 生成';
</script>
</body>
</html>
"""

HTML = HTML.replace("__DATE__", date).replace("__JSON__", json_str)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("WROTE", OUT, "total=", total, "sections=", [(s["label"], len(s["items"])) for s in sections_out])
