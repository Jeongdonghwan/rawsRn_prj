"""공통 문구 치환 (src/a·b·c.html 시안 소스 + static 서브페이지). 실행: python build_pages.py → build_final.py
멱등(여러 번 실행해도 같은 결과)."""
import re, os
H = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(H, "static")
loc = lambda f: os.path.join(H, "src", f[4:]) if f.startswith("src/") else os.path.join(R, f)
rd = lambda f: open(loc(f), encoding="utf-8").read()
wr = lambda f, s: open(loc(f), "w", encoding="utf-8").write(s)

# ---- 1. 사업자 정보 치환 (전 페이지) ----
REP = [
    ("법률사무소 알엠", "로펌 알엠 법률사무소"), ("RM LAW OFFICE", "LAW FIRM RM"),
    ("tel:0310000000", "tel:16447702"), ("031-000-0000", "1644-7702"),
    ("평일 09:00 – 18:00 (주말 예약제)", "24시간 상담 접수 (주말 예약제)"),
    ("평일 09:00 – 18:00 · 주말·야간 예약제", "24시간 상담 접수 · 주말 예약제"),
    ("평일 09:00 – 18:00", "24시간 상담 접수"),
    ("당일 상담 예약</div>", "24시간 상담 접수</div>"),
    ("평일 오전 접수 시 당일 상담. 주말·야간은 예약제로 운영합니다.", "밤낮 없이 접수하면 확인 즉시 연락드립니다. 주말은 예약제로 운영합니다."),
    ("당일<i>예약</i></div><div class=\"lbl\">평일 오전 접수 시 당일 상담", "24<i>시간</i></div><div class=\"lbl\">상담 접수 · 주말 예약제"),
    ("당일 안에 상담 일정을 잡습니다", "확인 즉시 상담 일정을 잡습니다"),
    ("<span><b>법률상담접수</b> 1644-7702</span>", "<span><b>법률상담접수</b> 1644-7702</span><span><b>이메일</b> lfrm2026@naver.com</span>"),
    ("<dt>전화</dt><dd>1644-7702</dd>", "<dt>전화</dt><dd>1644-7702</dd>\n          <dt>이메일</dt><dd>lfrm2026@naver.com</dd>"),
    ('<div class="tel">1644-7702</div>', '<div class="tel">1644-7702</div><p>lfrm2026@naver.com</p>'),
]
CLIENTS = ["주식회사 동후디앤씨", "주식회사 미디어솔루션", "주식회사 세오", "주식회사 테라", "주식회사 우성크라이어텍", "이디씨라이프 주식회사",
           "원광운수 주식회사", "합자회사 합동운수", "성남중앙지하상가상인회", "블랙다이아몬드커머디티스 유한회사", "아슨코리아 유한회사", "주식회사 푸른공조",
           "주식회사 에스오에스", "주식회사 선진메디칼", "주식회사 삼일종합건설", "주식회사 두손씨에스티"]
CLIENTS_HTML = '''  <!-- CLIENTS -->
  <section class="sec clients" id="clients">
    <div class="wrap">
      <div class="sec-head reveal"><h2>기업 법률자문</h2><p>로펌 알엠 법률사무소가 법률자문을 맡고 있는 기업과 단체입니다.</p></div>
      <ul class="reveal d1">
''' + "".join(f"        <li>{c}</li>\n" for c in CLIENTS) + '''      </ul>
    </div>
  </section>

'''
VIDEO = '<video class="bg" autoplay muted loop playsinline poster="img/hero-bg.webp" data-day="video/hero-day.mp4" data-night="video/hero-night.mp4"></video>'
vid = lambda h: h.replace('<img class="bg" src="img/hero-bg.webp" alt="">', VIDEO)
for f in ["src/a.html", "src/b.html", "src/c.html", "cases.html", "news.html", "practice.html"]:
    s = vid(rd(f))
    for a, b in REP:
        if b not in s: s = s.replace(a, b)
    s = re.sub(r'(<span><b>이메일</b> lfrm2026@naver.com</span>)+', r'\1', s)
    s = re.sub(r'(<dt>이메일</dt><dd>lfrm2026@naver.com</dd>\s*)+', r'\1', s)
    s = re.sub(r'(<p>lfrm2026@naver.com</p>)+', r'\1', s)
    if "<!-- CLIENTS -->" not in s:
        mark = "  <!-- CASES -->" if "  <!-- CASES -->" in s else ("  <!-- 의뢰인 후기" if "  <!-- 의뢰인 후기" in s else None)
        if mark: s = s.replace(mark, CLIENTS_HTML + mark, 1)
    wr(f, s)
js = rd("js/main.js")
for a, b in REP[:4]: js = js.replace(a, b)
wr("js/main.js", js)
css = rd("css/style.css")
css = css.replace(".hero img.bg {", ".hero .bg {")
if ".clients ul" not in css:
    css += """
/* 기업 법률자문 */
.clients ul { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.clients li { border: 1px solid var(--line); background: #fff; padding: 20px 16px; text-align: center; font-weight: 600; font-size: 15px; border-radius: 4px; }
@media (max-width: 760px) { .clients ul { grid-template-columns: 1fr 1fr; } .clients li { font-size: 13px; padding: 14px 8px; } }
.hero video.bg { animation: none; }
"""
    wr("css/style.css", css)
