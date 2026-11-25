"""메인 static/index.html + consult.html + profile.html 조립: src/b.html 기반 + src/c.html 블록.
실행: python build_final.py (build_pages.py 다음에)"""
import re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
rd = lambda f: open(os.path.join(R, f), encoding="utf-8").read()
src = lambda f: open(os.path.join(R, "..", "src", f), encoding="utf-8").read()
QUICK = """<div class="quick">
  <a class="q-t" href="tel:16447702"><em>전화상담</em><svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg><b>1644<i>-</i>7702</b></a>
  <div class="q-w">
    <a class="kakao q-k" href="#"><span><svg viewBox="0 0 24 24"><path d="M12 4C6.5 4 3 7.3 3 11c0 2.3 1.5 4.3 3.8 5.5L6 20l4-2.3c.6.1 1.3.2 2 .2 5.5 0 9-3.3 9-7s-3.5-7-9-7z"/></svg></span>카톡 상담</a>
    <a class="q-f" href="consult.html"><span><svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4zM8 9h8M8 12h5"/></svg></span>간편상담</a>
  </div>
  <a class="q-top" href="#" aria-label="맨 위로"><svg viewBox="0 0 24 24"><path d="M12 7l7 9H5z"/></svg>TOP</a>
</div>
"""
def quick(s):  # 우측 플로팅: 전화(번호) + 카톡·간편상담 + TOP. 모든 페이지 공통
    i, j = s.find('<div class="quick">'), s.find('<div class="mbar">')
    return s if i < 0 else s[:i] + QUICK + s[j:]
wr = lambda f, s: open(os.path.join(R, f), "w", encoding="utf-8").write(quick(s))
B, C, T = src("b.html"), src("c.html"), rd("cases.html")

def sec(src, key, tag="section"):
    m = re.search(rf'<{tag}[^>]*(?:id="{key}"|class="{key}[" ])[^>]*>.*?</{tag}>', src, re.S)
    assert m, key
    return m.group(0)

def cut(src, comment, block):  # "  <!-- 주석 -->\n  <section>" 통째로 제거
    out = re.sub(r"  <!-- " + comment + r"[^\n]*\n  " + re.escape(block) + r"\n+", "", src)
    assert out != src, comment
    return out

def hdr(s):  # 상단 검은 띠 삭제, 메뉴 3개(대표변호사·업무분야·업무사례)만, 메가메뉴 열도 맞춤
    s = re.sub(r'<div class="topbar">.*?\n', "", s, count=1)
    s = re.sub(r'      <a href="[^"]*">(소식·자료|상담신청|오시는 길)</a>\n', "", s)
    s = re.sub(r'      <ul><li><a href="[^"]*">(언론보도|온라인 상담|주소 · 지도)</a>.*?</ul>\n', "", s)
    assert "topbar" not in s and "소식·자료</a>" not in s[:s.index("</header>")]
    return s
P = hdr(B)
# 1. 인트로 큰 사진 → 분야 벤토 (형사·민사·가사 한 줄씩 + 행정·노무 반반)
intro = sec(B, "intro")
grid = re.search(r'(      <div class="grid">.*?\n      </div>)\n    </div>\n  </section>', sec(C, "attorney"), re.S).group(1)
big = re.search(r'        <a class="big.*?</a>\n', grid, re.S).group(0)
cards = re.findall(r'        <div class="card reveal.*?\n        </div>\n', grid, re.S)
assert len(cards) == 4, len(cards)
def card(cls, h3, p, pic, more):  # 배경 사진 하나 + 제목·소개, 카드 전체가 링크
    return f'        <a class="card bg {cls} reveal" href="{more}"><img src="img/{pic}.webp" alt="" loading="lazy"><div class="t"><h3>{h3}</h3><p>{p}</p></div></a>\n'
def row(c):  # C안 카드에서 제목·소개·사진·링크만 뽑아 한 줄 카드로
    h3, p, pic, more = [re.search(x, c, re.S).group(1) for x in (r'<h3>(.*?)</h3>', r'<p>(.*?)</p>', r'<img src="img/(.*?)\.webp', r'class="more" href="([^"]+)"')]
    return card("row", h3, p, pic, more)
newgrid = ('      <div class="grid">\n' + big + row(cards[0]) + row(cards[1]) + row(cards[3])
           + card("half", "행정", "영업정지·면허취소 같은 처분에 대한 행정심판과 행정소송. 인허가와 과징금 대응까지.", "s-towers", "practice.html")
           + card("half", "노무", "부당해고·임금체불·산재. 노사관계 분쟁 자문 경험으로 근로자와 사업주 양쪽을 압니다.", "s-meeting", "practice.html")
           + '      </div>')
assert newgrid.count('class="card bg') == 5
intro2 = re.sub(r'      <div class="big reveal d2">.*?    </div>\n  </section>',
                '    </div>\n  </section>\n\n  <section class="c-bento"><div class="wrap">\n' + newgrid.replace("\\", "\\\\") + '\n  </div></section>', intro, flags=re.S)
assert intro2 != intro
P = P.replace(intro, intro2)
# 인트로 제목: 상호 + LAW FIRM RM 가운데
P = P.replace('      <div class="eyebrow reveal">LAW FIRM RM · WIRYE, SEONGNAM</div>\n      <h2 class="reveal d1">로펌 알엠 법률사무소 소개</h2>',
              '      <h2 class="reveal">로펌 알엠 법률사무소<small>LAW FIRM RM</small></h2>')
assert "<small>LAW FIRM RM</small></h2>" in P

# 2·4. 수치 4칸, 경쟁력 교차 섹션 삭제
P = P.replace(sec(B, "b-stats"), "")
P = cut(P, "경쟁력", sec(B, "edge"))

# 3. 소개 바로가기 탭 삭제 (인사말·발자취가 profile.html 로 빠져 남는 항목이 없음)
P = re.sub(r'  <nav class="b-tabs".*?</nav>\n+', "", P, flags=re.S)
P = re.sub(r'\n<script>\n// B: 앵커 탭.*?</script>\n', "", P, flags=re.S)
assert "b-tabs" not in P

# 인사말·발자취는 메인에서 빼고 profile.html 로 (2차 수정 요청)
greet = sec(B, "attorney")
career = re.search(r'          <ul class="career">.*?</ul>\n', greet, re.S).group(0)
hist = sec(B, "history")
histin = re.search(r'<div class="wrap">\n(.*?)\n    </div>\n  </section>$', hist, re.S).group(1)
strip = re.search(r'<div class="strip reveal">.*?\n      </div>', histin, re.S).group(0)
cols = re.search(r'<ul class="cols">.*?</ul>', histin, re.S).group(0)
# 오른쪽 글 아래 발자취 표(빈 공간 채움), 사진 3장은 2단 아래 전체 폭
histblk = ('          <div class="b-hist" id="history"><h2>대표변호사 발자취</h2>\n          ' + cols
           + '\n          <p style="margin-top:32px"><a class="pill sm arrow" href="profile.html">대표변호사 약력 자세히 보기</a></p></div>\n')
P = cut(P, "인사말", greet)
P = cut(P, "발자취", hist)

# 5. 남색 띠 삭제 → 상담 절차 + 인용 2단을 벤토와 인사말 사이로 (슬라이더 없음)
steps = sec(C, "practice").replace('id="practice"', 'id="steps"')
a = '<a class="more" href="#apply">상담 신청</a></div>'  # 제목 옆 링크 삭제 (수정요청)
assert steps.count(a) == 1
steps = steps.replace(a, '</div>')
quote = '''  <section class="b-quote" id="phil">
    <div class="wrap">
      <div class="mark reveal"><span class="mk">R<i>M</i></span><p><b>로펌 알엠 법률사무소</b>Risk &amp; Management — 위험을 먼저 읽고, 끝까지 관리합니다. 의뢰인이 가장 힘든 순간에 곁에 있는 법률사무소가 되겠다는 뜻을 담았습니다.</p></div>
    </div>
  </section>'''
P = cut(P, "철학", sec(B, "phil"))
assert P.count('\n  </div></section>\n') == 1  # 벤토 끝
P = P.replace('\n  </div></section>\n', '\n  </div></section>\n\n  <!-- 상담 절차 -->\n' + steps + "\n\n  <!-- 철학 -->\n" + quote + '\n', 1)
assert "b-greet" not in P

# 6. 의뢰인 이야기 → CASES 안으로 합침 (4칸 한 줄)
revs = re.findall(r'<a class="r reveal[^"]*".*?</a>', sec(C, "media"), re.S)
assert len(revs) == 4
rev4 = ('      <div class="c-rev sub">\n        <div class="head"><h2>의뢰인 이야기</h2><p>직접 상담하고 진행한 분들의 말 (예시 문구)</p></div>\n        <div class="inner">\n'
        + "".join("          " + r + "\n" for r in revs) + '        </div>\n      </div>\n')
anchor = '      <div class="cases" id="home-cases"></div>\n'
assert anchor in P
P = P.replace(anchor, anchor + rev4)

# 7. 갤러리 → MEDIA 안으로 합침
gal = re.search(r'(<div class="head">.*?\n      </div>)\n    </div>\n  </section>', sec(C, "news"), re.S).group(1).replace('href="#attorney"', 'href="profile.html"')
media = sec(B, "media")
media2 = media.replace('\n    </div>\n  </section>', '\n      <div class="c-gal reveal">' + gal + '</div>\n    </div>\n  </section>')
assert media2 != media
P = P.replace(media, media2)

# 언론보도·법률정보 삭제 (+ 스크립트)
P = cut(P, "NEWS", sec(B, "news"))
P = re.sub(r"fetch\('data/news\.json'\).*?\n\}\);\n", "", P, flags=re.S)
assert "home-press" not in P

# 상담 문의: 영문 제목 삭제, 두 번째 카드 '상담신청'
P = P.replace('<h2 class="en">CONSULTING</h2>', '<h2>상담 문의</h2>').replace('<h2 class="en">CASES</h2>', '<h2>사건사례</h2>').replace('<h2 class="en">MEDIA</h2>', '<h2>방송·미디어</h2>').replace('<h3>온라인 문의</h3>', '<h3>상담신청</h3>')

# 상담 신청 폼 → consult.html, 메인은 오시는 길만 가로로 길게
apply = sec(B, "apply")
form = re.search(r'      <div class="reveal">\n        <h2>온라인 상담 신청</h2>.*?</form>\n      </div>\n', apply, re.S).group(0)
loc = apply.replace(form, "").replace('<section class="sec apply" id="apply">', '<section class="sec apply loc" id="visit">').replace('<div class="wrap inner">', '<div class="wrap">')
P = P.replace(apply, loc)

# 푸터 링크 묶음 삭제
P = re.sub(r'    <div class="top">.*?\n    </div>\n', "", P, flags=re.S)

# 링크: 상담신청 → consult.html, 대표변호사 메뉴 → profile.html
P = P.replace('href="#apply"', 'href="consult.html"').replace('href="#attorney">대표변호사</a>', 'href="profile.html">대표변호사</a>').replace('href="#attorney">주요 경력', 'href="profile.html">주요 경력')


# 강점 4가지 (벤토 바로 아래, 시안 A 밝게 / B 카드). 문구는 B안 '경쟁력'에서 가져옴
NL = chr(10)
edge = re.findall(r'<div class="n">(.*?)</div><h3>(.*?)</h3><p>(.*?)</p>', B)[:4]
assert len(edge) == 4
why = ('  <section class="f-why" id="why">' + NL + '    <div class="wrap">' + NL
       + '      <div class="l reveal"><small>WHY RM</small><h2>큰 로펌의 경험을,<br>가까운 거리에서<br>직접 수행합니다.</h2><p>상담부터 변론까지 대표변호사가 맡습니다. 특검 사건 변호와 상장기업 자문으로 쌓은 경험을 개인 의뢰인의 사건에 그대로 씁니다.</p></div>' + NL
       + '      <ol>' + NL + "".join(f'        <li class="reveal"><i>{n}</i><h3>{h}</h3><p>{p}</p></li>' + NL for n, h, p in edge) + '      </ol>' + NL + '    </div>' + NL + '  </section>')
a = NL + NL + '  <!-- 상담 절차 -->' + NL
assert P.count(a) == 1
P = P.replace(a, NL + NL + '  <!-- 강점 -->' + NL + why + a)

# 업무분야 큰 카드: 알엠 이야기 → 기업
a = '<div class="t"><small>알엠 이야기</small><h3>사무장이 아닌 변호사가<br>직접 듣고 직접 변론합니다</h3></div>'
assert P.count(a) == 1
P = P.replace(a, '<div class="t"><small>CORPORATE LAW</small><h3>기업</h3><p>상장기업 법률자문과 M&amp;A, 공정거래, 기업회생까지. 분쟁이 되기 전에 위험을 먼저 읽고, 소송이 되면 대표변호사가 직접 변론합니다.</p></div>')
a = '<a class="big reveal" href="consult.html">'
assert P.count(a) == 1
P = P.replace(a, '<a class="big reveal" href="corporate/index.html">')
for h3, k in [("형사", "criminal"), ("민사", "civil"), ("가사", "family"), ("행정", "admin"), ("노무", "labor")]:  # 벤토 카드 → 센터
    P, n = re.subn(r'(<a class="card bg [^"]*" href=")[^"]*("><img [^>]*><div class="t"><h3>' + h3 + '</h3>)', lambda m: m.group(1) + k + "/index.html" + m.group(2), P)
    assert n == 1, h3

# 업무분야 세부 목록 (벤토 바로 아래). 항목은 의뢰인 레퍼런스 그대로
# 항목 → 상세 페이지 주소 (practice-{slug}.html). 글은 src/fields.json
SLUG = {"기업일반": "corp-general", "국제법무·중재": "intl-arbitration", "경영법무컨설팅": "mgmt-consulting", "공정거래": "fair-trade",
        "기업회생·파산·M&amp;A": "restructuring-ma", "금융·자본시장": "finance-capital", "AI·데이터인텔리전스": "ai-data", "지식재산권": "ip",
        "엔터테인먼트·스포츠": "ent-sports", "의료·바이오·헬스케어": "healthcare", "방위산업": "defense",
        "형사": "criminal", "기업형사·화이트칼라범죄": "white-collar", "성범죄": "sex-crime", "음주·교통사고": "dui-traffic", "마약": "drugs", "특별수행본부": "special-task",
        "민사": "civil", "건설·부동산": "construction-realestate", "가사": "family", "이혼": "divorce", "상속": "inheritance",
        "헌법·행정·규제개혁": "admin-constitutional", "국제조세·관세": "tax-customs", "학교폭력대응": "school-violence", "외국인소송": "foreigner",
        "노동·산재": "labor-injury", "중대재해": "serious-accident"}
page = lambda it: f"practice-{SLUG[it]}.html"
GK = {"기업소송": "corporate", "형사소송": "criminal", "민사소송": "civil", "가사 및 이혼소송": "family", "행정소송": "admin", "노무소송": "labor"}  # 그룹 → 센터 폴더 (추후 별도 도메인)
AREAS = [
    ("CORPORATE LAW", "기업소송", "practice.html", "M3 21h18M5 21V7l7-4 7 4v14M9 9h1M14 9h1M9 13h1M14 13h1M9 17h1M14 17h1",
     ["기업일반", "국제법무·중재", "경영법무컨설팅", "공정거래", "기업회생·파산·M&amp;A", "금융·자본시장", "AI·데이터인텔리전스", "지식재산권", "엔터테인먼트·스포츠", "의료·바이오·헬스케어", "방위산업"]),
    ("CRIMINAL LAW", "형사소송", "practice.html#criminal", "M12 3v18M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0zM8 21h8",
     ["형사", "기업형사·화이트칼라범죄", "성범죄", "음주·교통사고", "마약", "특별수행본부"]),
    ("CIVIL LAW", "민사소송", "practice.html#civil", "M6 3h9l4 4v14H6zM15 3v4h4M9 12h6M9 16h6",
     ["민사", "건설·부동산"]),
    ("FAMILY &amp; DIVORCE LAW", "가사 및 이혼소송", "practice.html#family", "M3 11l9-7 9 7M5 10v10h14V10M10 20v-5h4v5",
     ["가사", "이혼", "상속"]),
    ("ADMINISTRATIVE LAW", "행정소송", "practice.html", "M3 21h18M4 10h16M12 3l9 5H3zM6 10v8M10 10v8M14 10v8M18 10v8",
     ["헌법·행정·규제개혁", "국제조세·관세", "학교폭력대응", "외국인소송"]),
    ("LABOR &amp; EMPLOYMENT LAW", "노무소송", "practice.html", "M4 14a8 8 0 0 1 16 0zM2 14h20M12 6V4M9 18h6",
     ["노동·산재", "중대재해"]),
]
toggle = "const o=this.parentNode.classList.toggle('open');this.setAttribute('aria-expanded',o);this.firstChild.textContent=o?'접기':'전체 보기'"
areas = ('  <section class="f-areas" id="areas">' + NL + '    <div class="wrap">' + NL
         + '      <nav class="ctr reveal"><span>센터 바로 이동</span>' + "".join(f'<a href="{GK[ko]}/index.html">{ko.replace("소송", "").replace(" 및 이혼", "·이혼")}센터</a>' for en, ko, href, ico, items in AREAS) + '</nav>' + NL
         + '      <div class="box"><div class="grid">' + NL
         + "".join(f'        <div class="ar reveal"><div class="top"><i>{n:02d}</i><div><small>{en}</small><h3>{ko}</h3></div><a class="go" href="{GK[ko]}/index.html" aria-label="{ko} 센터로 이동"><span>센터 보기</span><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></div><ul>'
                   + "".join(f'<li><a href="{page(it)}">{it}<b></b></a></li>' for it in items) + '</ul></div>' + NL
                   for n, (en, ko, href, ico, items) in enumerate(AREAS, 1))
         + f'      </div><button class="more" type="button" aria-expanded="false" onclick="{toggle}"><span>전체 보기</span><svg viewBox="0 0 24 24"><path d="M12 5v14M6 13l6 6 6-6"/></svg></button></div>' + NL
         + '      PCARDS' + NL
         + '    </div>' + NL + '  </section>')
# 업무분야 사진 카드 시안 (의뢰인 참고 파일 마지막.html = A, fullscreen.html = B). 제목 → 센터, 세부 항목 → 상세 페이지
GIMG = {"corporate": "img/s-hall.webp", "criminal": "img/n/criminal.webp", "civil": "img/n/justice-statue.webp",
        "family": "img/s-family.webp", "admin": "img/n/city-dusk.webp", "labor": "img/n/labor-shake.webp"}
PDESC = {"corporate": "상장기업 법률자문과 M&amp;A, 공정거래, 기업회생까지. 분쟁이 되기 전에 위험을 먼저 읽습니다.",
         "criminal": "경찰 조사 동석부터 영장심사, 공판까지. 특검 사건을 다수 변호한 대표변호사가 직접 맡습니다.",
         "civil": "계약·손해배상·건설·부동산 분쟁. 소송 전 증거 정리부터 판결 뒤 회수까지 설계합니다.",
         "family": "이혼·재산분할·양육권·상속. 의뢰인과 자녀의 내일을 먼저 생각합니다.",
         "admin": "영업정지·면허취소 같은 처분에 대한 행정심판과 행정소송. 조세·학교폭력·외국인 사건까지.",
         "labor": "부당해고·임금체불·산재·중대재해. 노사관계 분쟁 자문 경험으로 근로자와 사업주 양쪽을 압니다."}
def pcard(en, ko, items, b):
    k, nm = GK[ko], ko.replace("소송", "").replace(" 및 이혼", "·이혼")
    subs = '<ul class="subs">' + "".join(f'<li><a href="{page(it)}">{it}</a></li>' for it in items) + '</ul>'
    t = f'<small>{en}</small><h3><a href="{k}/index.html" title="{nm} 센터로 이동">{nm}<span class="to">센터 사이트 →</span></a></h3><p>{PDESC[k]}</p>'
    return (f'<article class="pc" tabindex="0" style="background-image:url({GIMG[k]})"><div class="tx">{t}'
            + (f'</div>{subs}' if b else f'<div class="sw"><div class="si">{subs}</div></div></div>') + '</article>')
PB_JS = """(()=>{const g=document.querySelector('.pg.pb');let t,cur;
const px=c=>({top:c.offsetTop+'px',left:c.offsetLeft+'px',width:c.offsetWidth+'px',height:c.offsetHeight+'px'});
const close=()=>{if(!cur)return;const o=cur,c=o.card;cur=null;o.classList.remove('on');c.dataset.lock=1;Object.assign(o.style,px(c));setTimeout(()=>{o.remove();if(!c.matches(':hover'))delete c.dataset.lock},600)};
const open=c=>{if(cur||c.dataset.lock)return;const o=document.createElement('div');o.className='fs';Object.assign(o.style,px(c));o.style.backgroundImage='linear-gradient(rgba(13,22,40,.55),rgba(13,22,40,.88)),'+c.style.backgroundImage;
o.innerHTML='<button class="x" type="button" aria-label="닫기">×</button><div class="fsin">'+c.querySelector('.tx').innerHTML+c.querySelector('.subs').outerHTML+'</div>';
g.append(o);o.offsetHeight;o.classList.add('on');Object.assign(o.style,{top:0,left:0,width:'100%',height:'100%'});o.querySelector('.x').onclick=close;o.onmouseleave=close;o.card=c;cur=o};
g.querySelectorAll('.pc').forEach(c=>{c.onmouseenter=()=>{if(c.dataset.lock)return;clearTimeout(t);t=setTimeout(()=>open(c),280)};c.onmouseleave=()=>{clearTimeout(t);if(!cur)delete c.dataset.lock};
c.onclick=e=>{if(!e.target.closest('a')){clearTimeout(t);open(c)}};c.onkeydown=e=>{if(e.key==='Enter'&&e.target===c)open(c)}});
addEventListener('keydown',e=>{if(e.key==='Escape')close()});
const s=document.getElementById('areas'),pick=v=>{s.dataset.v=v;s.querySelectorAll('.vsw button').forEach(b=>b.classList.toggle('on',b.dataset.v===v))};
s.querySelectorAll('.vsw button').forEach(b=>b.onclick=()=>pick(b.dataset.v));pick(new URLSearchParams(location.search).get('pa')||'a')})();"""
areas = areas.replace('<section class="f-areas" id="areas">', '<section class="f-areas" id="areas" data-v="a">').replace(
    '<div class="box">', '<div class="vsw"><span>업무분야 시안</span><button type="button" data-v="a">A 올라오는 목록</button><button type="button" data-v="b">B 화면 확장</button><button type="button" data-v="c">기존 목록</button></div>' + NL + '      <div class="box">').replace(
    'PCARDS', '<div class="pg pa reveal">' + "".join(pcard(en, ko, items, 0) for en, ko, href, ico, items in AREAS) + '</div>' + NL
    + '      <div class="pg pb reveal">' + "".join(pcard(en, ko, items, 1) for en, ko, href, ico, items in AREAS) + '</div>' + NL
    + f'      <script>{PB_JS}</script>')

# 배너 사진 교체, 방송·미디어 사진 자리에 유튜브
a = '<img src="img/s-skyline.webp" alt="" loading="lazy">'
assert P.count(a) == 1
P = P.replace(a, a.replace("s-skyline", "s-boardroom"))
YT = ""  # 유튜브 영상 ID 를 받으면 여기에 (예: "dQw4w9WgXcQ")
a = '<div class="pic reveal"><img src="img/media.webp" alt="" loading="lazy"></div>'
assert P.count(a) == 1
P = P.replace(a, '<div class="pic yt reveal">' + (f'<iframe src="https://www.youtube-nocookie.com/embed/{YT}" title="로펌 알엠 유튜브" loading="lazy" allowfullscreen></iframe>' if YT
              else '<div class="ph"><svg viewBox="0 0 68 48"><rect width="68" height="48" rx="12"/><path d="M27 14l18 10-18 10z"/></svg><b>유튜브 영상 자리</b><small>영상 주소를 받으면 이 자리에서 바로 재생됩니다</small></div>') + '</div>')

# 인트로 문구 강조
a = '대표변호사가 직접 듣고 직접 변론합니다</p>'
assert P.count(a) == 1
P = P.replace(a, '대표변호사가 <b>직접 듣고 직접 변론</b>합니다</p>')

# 메인의 '알엠 법률 서비스' 섹션은 숨김 (final.css), 그쪽 링크는 업무분야 페이지로
P = P.replace('href="#practice"', 'href="practice.html"')

# 새 사진 (사진 시안 B, 기본). src = 새 사진, data-o = 기존 사진 → 전환 버튼 A 로 되돌림
def newimg(s, pairs):  # (그 줄에만 있는 글자, 새 파일명): 줄의 첫 <img> 교체
    L = s.split(NL); hit = {}
    for n, line in enumerate(L):
        for k, new in pairs:
            if k in line and '<img src="img/' in line:
                assert k not in hit, k
                hit[k] = 1
                L[n] = re.sub(r'<img src="(img/[^"]+)"', lambda m: f'<img src="img/n/{new}.webp" data-o="{m.group(1)}"', line, count=1)
                break
    assert len(hit) == len(pairs), set(k for k, _ in pairs) - set(hit)
    return NL.join(L)
P = newimg(P, [("img/s-gavel.", "criminal"), ("img/s-justice.", "justice-statue"),
               ("<h3>행정</h3>", "city-dusk"), ("<h3>노무</h3>", "labor-shake"),
               ("img/s-hands-doc.", "step-suit"), ("img/s-sign.", "step-talk"), ("img/s-court.", "step-shake"),
               ("img/s-consult.", "story-key"), ("img/s-handshake.", "story-arch"), ("img/s-typing.", "story-hall"), ('f=가사"><div class="pic">', "story-stairs")])

# 머리·스크립트
P = P.replace('<link rel="stylesheet" href="css/b.css">', '<link rel="stylesheet" href="css/b.css">\n<link rel="stylesheet" href="css/c.css">\n<link rel="stylesheet" href="css/final.css">')
P = re.sub(r"<title>.*?</title>", "<title>로펌 알엠 법률사무소 | 성남 위례 형사·민사·가사 전문</title>", P)
P = P.replace("<body>", '<body class="final" data-bento="b">', 1)  # 분야 카드는 세로형 확정
rails = """<nav class="abc">
<span>메뉴</span><a data-k="gnb" data-v="a">A 가운데</a><a data-k="gnb" data-v="b">B 오른쪽</a>
<span>영상</span><a data-k="vid" data-v="t">1→2 연속</a><a data-k="vid" data-v="4">밤하늘</a><a data-k="vid" data-v="5">노을</a><a data-k="vid" data-v="a">기존</a><a data-k="vid" data-v="1">1 낮 도심</a><a data-k="vid" data-v="2">2 밤 도심</a><a data-k="vid" data-v="3">3 유리 빌딩</a>
<span>사진</span><a data-k="img" data-v="a">A 기존</a><a data-k="img" data-v="b">B 새 사진</a>
<span>강점</span><a data-k="why" data-v="a">A 밝게</a><a data-k="why" data-v="b">B 카드</a>
</nav>
<script>
// 시안 전환: body[data-gnb|bento|why]. 확정되면 기본값만 남기고 삭제
const pick = (k, v) => { document.body.dataset[k] = v; document.querySelectorAll('.abc a[data-k=' + k + ']').forEach(a => a.classList.toggle('on', a.dataset.v === v)); try { localStorage['rm2-' + k] = v; } catch (e) {}
  if (k === 'vid') window.heroVid?.();
  if (k === 'img') document.querySelectorAll('img[data-o]').forEach(i => { i.dataset.n ||= i.getAttribute('src'); i.src = v === 'a' ? i.dataset.o : i.dataset.n; }); };
document.querySelectorAll('.abc a').forEach(a => a.onclick = () => pick(a.dataset.k, a.dataset.v));
// 확정: 메뉴 B 오른쪽 · 영상 1 밤하늘 → 2 노을 연속 재생 · 사진 B · 강점 A. 버튼은 숨김, 주소에 ?abc 붙이면 다시 보임
const q = new URLSearchParams(location.search); if (q.has('abc')) document.querySelector('.abc').classList.add('show');
Object.entries({ gnb: 'b', vid: 't', img: 'b', why: 'a' }).forEach(([k, d]) => pick(k, q.get(k) || d));
</script>
""" + '''<script>
document.querySelectorAll('[data-rail-prev],[data-rail-next]').forEach(b => b.onclick = () => {
  const r = document.querySelector(b.dataset.railPrev || b.dataset.railNext);
  r.scrollBy({ left: (b.dataset.railPrev ? -1 : 1) * r.clientWidth * .8, behavior: 'smooth' });
});
</script>
'''
P = P.replace('<script src="js/main.js"></script>', rails + '<script src="js/main.js"></script>')

ids = re.findall(r' id="([^"]+)"', P)
dup = {i for i in ids if ids.count(i) > 1}
assert not dup, dup
wr("index.html", P)
print("built index.html", len(P))

# ---- 서브 페이지 (cases.html 틀) ----
head = T[:T.index('<section class="sub-hero">')]
foot = T[T.index('<footer>'):]
for a, b in [('href="./#apply"', 'href="consult.html"'), ('href="./#attorney">대표변호사', 'href="profile.html">대표변호사'), ('href="./#attorney">주요 경력', 'href="profile.html">주요 경력'), ('href="./#consult"', 'href="consult.html"')]:
    head, foot = head.replace(a, b), foot.replace(a, b)
foot = re.sub(r'    <div class="top">.*?\n    </div>\n', "", foot, flags=re.S)
head = hdr(head)
head, foot = head.replace('href="./#practice"', 'href="practice.html"'), foot.replace('href="./#practice"', 'href="practice.html"')
for f in ("cases.html", "news.html", "practice.html"): wr(f, hdr(rd(f)))  # 서브페이지 머리도 동일하게
# 업무분야 페이지: 상단 소개 아래에 분야별 세부 목록 (다시 실행해도 한 번만 들어가게 표시 주석 사이를 교체)
pr = re.sub(r'<!-- 업무분야 세부 -->.*?<!-- /업무분야 세부 -->' + NL, '', rd("practice.html"), flags=re.S)
a = '<div class="wrap areas">'
assert pr.count(a) == 1
pr = pr.replace(a, '<!-- 업무분야 세부 -->' + NL + areas + NL + '<!-- /업무분야 세부 -->' + NL + a)
# 머리: 예전 '개인 고객' 소개 → 업무분야 소개 한 덩어리 (베이지)
pr = re.sub(r'<section class="sub-hero[^"]*">.*?</section>', '''<section class="sub-hero pr-hero">
  <div class="wrap">
    <div class="crumb">⌂ &nbsp;›&nbsp; <b>업무분야</b></div>
    <div class="lab">PRACTICE AREAS</div>
    <h1>업무분야</h1>
    <p>기업부터 개인까지, 6개 센터의 분야별 사건을 변환봉 대표변호사가 직접 맡습니다.<br>분야를 누르면 진행 절차와 자주 묻는 질문을 볼 수 있습니다.</p>
  </div>
</section>''', pr, count=1, flags=re.S)
pr = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="로펌 알엠 업무분야 - 기업·형사·민사·가사·행정·노무 6개 센터와 세부 분야 28개. 분야별 진행 절차와 자주 묻는 질문, 상담 1644-7702.">', pr, count=1)
a = '<link rel="stylesheet" href="css/style.css">'
if 'css/final.css' not in pr: pr = pr.replace(a, a + NL + '<link rel="stylesheet" href="css/final.css">', 1)
wr("practice.html", pr)
def sub(name, title, desc, lab, h1, p, body, css="", cta=True):
    h = head.replace('<link rel="stylesheet" href="css/style.css">', '<link rel="stylesheet" href="css/style.css">' + css)
    h = re.sub(r"<title>.*?</title>", f"<title>{title} | 로펌 알엠 법률사무소</title>", h)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h)
    hero = f'''<section class="sub-hero">
  <div class="wrap">
    <div class="crumb">⌂ &nbsp;›&nbsp; <b>{title}</b></div>
    <div class="lab">{lab}</div>
    <h1>{h1}</h1>
    <p>{p}</p>
  </div>
</section>

'''
    c = '<section class="sub-cta">\n  <h2>비슷한 상황이신가요?</h2>\n  <a href="consult.html" class="pill arrow">상담 신청</a>\n</section>\n\n' if cta else ""
    wr(name, h + hero + body + "\n\n" + c + foot)
    print("built", name)

sub("consult.html", "상담 신청", "로펌 알엠 법률사무소 온라인 상담 신청. 24시간 접수, 대표변호사가 직접 확인하고 연락드립니다.",
    "CONSULTING", "상담 신청", "사건 개요를 남겨주시면 대표변호사가 직접 확인하고 연락드립니다. 전화 1644-7702, 카카오톡 채널로도 24시간 접수합니다.",
    apply.replace('<section class="sec apply" id="apply">', '<section class="sec apply" id="apply" style="padding-top:40px">'), cta=False)

# 약력 페이지: 메인과 같은 2단(글 + 발자취 표), 아래에 사진 3장 (상담실 사진 자리에)
wide = re.search(r'      <div class="wide reveal">.*?</div>\n      </div>\n', greet, re.S).group(0)
pg = greet.replace(career, re.sub(r'\n          <p style="margin-top:32px">.*?</p>', "", histblk)).replace(wide, '      <div class="b-hist pics">' + strip + '</div>\n')
pg = pg.replace('<section class="b-greet" id="attorney">', '<section class="b-greet" id="attorney" style="padding-top:40px">')
assert strip in pg and cols in pg
sub("profile.html", "대표변호사", "로펌 알엠 법률사무소 대표변호사 변환봉 약력. 사법시험 합격, 前 서울지방변호사회 사무총장, 로스쿨 출강, 상장기업 법률자문, 특검 사건 변호.",
    "PROFILE", "대표변호사 변환봉", "사법시험을 거쳐 변호사가 된 뒤 서울지방변호사회 사무총장, 로스쿨 출강, 상장기업 법률자문과 특검 사건 변호를 두루 경험했습니다.",
    pg, css='\n<link rel="stylesheet" href="css/b.css">\n<link rel="stylesheet" href="css/final.css">')
p = rd("profile.html").replace('<body class="sub">', '<body class="sub final">', 1)
p = newimg(p, [("img/s-lecture.", "library-book"), ("img/s-assembly.", "defense-seat"), ("img/s-library.", "bookshelf")])
wr("profile.html", p)


# ---- 업무분야 상세 페이지 28개: src/fields.json → static/practice-{slug}.html ----
# 형식은 programmatic-seo §5-1~5-4 (h1 수식어, title 40자, description 45~80자, 핵심 요약 + 번호 절 6 + FAQ 4, 최종 수정일)
# 구성은 대륜 업무분야 페이지 참고: 목차, 번호 소제목, 강점, 상담 예약 버튼, 관련 업무분야
import json, html as H
UPDATED = "2026-11-25"  # 상세 페이지 본문·title 을 바꾼 날로 올린다
FIELDS = json.load(open(os.path.join(R, "..", "src", "fields.json"), encoding="utf-8"))
FBY = {d["slug"]: d for d in FIELDS}
assert len(FBY) == len(SLUG) == 28 and set(FBY) == set(SLUG.values()), set(SLUG.values()) ^ set(FBY)
GROUPS = [(en, ko, [SLUG[it] for it in items]) for en, ko, href, ico, items in AREAS]
STR = [("대표변호사 직접 수행", "상담부터 서면 작성, 법정 출석까지 사무장이 아닌 대표변호사가 맡습니다."),
       ("상장기업 자문·M&amp;A", "코스피·코스닥 상장기업 법률자문과 M&amp;A를 다수 수행했습니다."),
       ("특검 사건 변호·방송 해설", "특검 사건을 다수 변호했고 MBC 100분토론 등 시사 프로그램에서 법률 해설을 해왔습니다.")]
ICO = {"tel": "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z",
       "form": "M6 3h9l4 4v14H6zM15 3v4h4M9 12h6M9 16h6",
       "talk": "M12 4C6.5 4 3 7.3 3 11c0 2.3 1.5 4.3 3.8 5.5L6 20l4-2.3c.6.1 1.3.2 2 .2 5.5 0 9-3.3 9-7s-3.5-7-9-7z"}
svg = lambda k: f'<svg viewBox="0 0 24 24"><path d="{ICO[k]}"/></svg>'
amp = lambda t: re.sub(r"&(?!amp;|lt;|gt;|quot;|#)", "&amp;", t)  # 글 속 & 를 HTML 로
text = lambda t: re.sub(r"<[^>]+>", "", H.unescape(t))

def fpage(d):
    g = next(x for x in GROUPS if d["slug"] in x[2])
    en, gko, slugs = g
    kw, sub_ = amp(d["kw"]), amp(d["h1sub"])
    secs = d["sections"]
    toc = "".join(f'<li><a href="#s{i}"><i>{i:02d}</i>{amp(x["h2"])}</a></li>' for i, x in enumerate(secs, 1))
    body = "".join(f'      <section class="fs" id="s{i}"><h2><i>{i:02d}</i>{amp(x["h2"])}</h2><p>{amp(x["p"])}</p></section>' + NL for i, x in enumerate(secs, 1))
    facts = "".join(f"<div><dt>{amp(k)}</dt><dd>{amp(v)}</dd></div>" for k, v in d["facts"])
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{amp(q["q"])}</summary><p>{amp(q["a"])}</p></details>' for i, q in enumerate(d["faq"]))
    same = [x for x in slugs if x != d["slug"]]
    rel1 = "".join(f'<a href="practice-{x}.html"><small>{gko}</small>{amp(FBY[x]["item"])}</a>' for x in same)
    rel2 = "".join(f'<a href="{GK[x[1]]}/index.html"><small>{x[0]}</small>{x[1]} 센터</a>' for x in GROUPS if x is not g)
    strs = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in STR)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": text(q["q"]), "acceptedAnswer": {"@type": "Answer", "text": text(q["a"])}} for q in d["faq"]]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate([("홈", "./"), ("업무분야", "practice.html"), (text(gko), f"{GK[gko]}/index.html"), (text(d["item"]), f"practice-{d['slug']}.html")], 1)]},
          {"@context": "https://schema.org", "@type": "WebPage", "name": text(d["title"]), "dateModified": UPDATED,
           "about": {"@type": "LegalService", "name": "로펌 알엠 법률사무소", "telephone": "1644-7702", "address": {"@type": "PostalAddress", "streetAddress": "위례광장로 322, 212호", "addressLocality": "성남시 수정구", "addressRegion": "경기도", "addressCountry": "KR"}}}]
    h = head.replace('<link rel="stylesheet" href="css/style.css">', '<link rel="stylesheet" href="css/style.css">\n<link rel="stylesheet" href="css/final.css">')
    h = re.sub(r"<title>.*?</title>", lambda m: f"<title>{amp(d['title'])}</title>", h)
    h = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{amp(d["desc"])}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{amp(d["title"])}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{amp(d["desc"])}">', h)
    h = h.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld) + "</head>", 1)
    main = f"""<main class="field">
<section class="sub-hero f-hero">
  <div class="wrap">
    <div class="crumb">⌂ &nbsp;›&nbsp; <a href="practice.html">업무분야</a> &nbsp;›&nbsp; <a href="{GK[gko]}/index.html">{gko}</a> &nbsp;›&nbsp; <b>{amp(d["item"])}</b></div>
    <p class="cat">{en} · {gko}</p>
    <h1><span>{kw}</span> <span class="hero-sub">{sub_}</span></h1>
    <p class="lead">{amp(d["lead"])}</p>
    <p class="upd">최종 수정 {UPDATED}</p>
  </div>
</section>

<div class="wrap f-body">
  <aside class="f-side">
    <div class="toc"><b>목차</b><ol>{toc}<li><a href="#faq"><i>Q</i>자주 묻는 질문</a></li></ol></div>
    <div class="now"><h3>바로 확인</h3><p>대표변호사가 직접 듣고 사건 방향을 안내합니다. 예상 비용과 범위는 상담 단계에서 서면으로 먼저 알려드립니다.</p>
      <a class="tel" href="tel:16447702">{svg("tel")}1644-7702</a><a href="consult.html">{svg("form")}온라인 상담 신청</a></div>
  </aside>
  <article class="f-main">
      <section class="sum"><h2>{kw} 핵심 요약</h2><p>{amp(d["summary"])}</p><dl>{facts}</dl></section>
{body}      <section class="faq" id="faq"><h2>{kw} 자주 묻는 질문</h2>{faq}</section>
  </article>
</div>

<section class="f-str">
  <div class="wrap">
    <h2>로펌 알엠의 강점</h2>
    <ul>{strs}</ul>
    <a class="more" href="profile.html">대표변호사 약력 보기</a>
  </div>
</section>

<section class="f-book">
  <div class="wrap">
    <h2>{kw} 상담 예약</h2>
    <p>전화는 24시간 접수합니다. 남겨주신 사건 개요는 대표변호사가 직접 확인하고 연락드립니다.</p>
    <div class="btns"><a href="tel:16447702">{svg("tel")}<b>전화 상담</b><small>1644-7702</small></a><a href="consult.html">{svg("form")}<b>온라인 상담</b><small>사건 개요 남기기</small></a><a class="kakao" href="#">{svg("talk")}<b>카카오톡 상담</b><small>채널로 간편 문의</small></a></div>
  </div>
</section>

<section class="f-rel">
  <div class="wrap">
    {f'<div class="blk"><h2>{gko}, 이어서 확인할 것</h2><div class="cards">{rel1}</div></div>' if rel1 else ""}
    <div class="blk"><h2>다른 업무분야</h2><div class="cards">{rel2}<a href="practice.html"><small>PRACTICE AREAS</small>업무분야 전체 보기</a><a href="cases.html"><small>CASES</small>업무사례 보기</a></div></div>
  </div>
</section>
</main>

"""
    wr(f"practice-{d['slug']}.html", h.replace('<body class="sub">', '<body class="sub field-page">', 1) + main + foot)

for d in FIELDS: fpage(d)
print("built practice-*.html", len(FIELDS))


# ---- 그룹 센터 미니사이트 6개: src/groups.json → static/{key}/index.html ----
# 나중에 그룹별 별도 도메인·서브도메인으로 뗄 예정 → 폴더 하나에 독립 페이지(자체 상단 메뉴·히어로·사례·후기·상담).
# 지금은 시안: 링크는 ../ 로 본 사이트 자원을 쓰고, 떼어낼 때 ../ 만 도메인 주소로 바꾸면 된다. 사례·후기는 예시(화면에 표시).
GKEY = ["corporate", "criminal", "civil", "family", "admin", "labor"]  # AREAS 순서와 같게
GROUPS_D = {d["key"]: d for d in json.load(open(os.path.join(R, "..", "src", "groups.json"), encoding="utf-8"))}
assert list(GROUPS_D) == GKEY, list(GROUPS_D)
GOF = {g[1]: k for g, k in zip(GROUPS, GKEY)}  # 그룹 한글명 → key
EXTRA = {"corporate": ["white-collar"]}  # 기업센터에서 같이 보여줄 다른 그룹 항목

def to_root(html_, up="../"):  # 본 사이트 기준 상대경로 → 한 단계 위
    return re.sub(r'(href|src)="(?!https?:|tel:|mailto:|#|\.\./|data:)([^"]*)"', lambda m: f'{m.group(1)}="{up}{m.group(2) or "./"}"', html_)

TOOLS = {
"family": """<section class="g-tool" id="tool"><div class="wrap"><div class="g-sh"><small>TOOL</small><h2>법정상속분 계산기</h2><p>가족 관계를 넣으면 민법이 정한 상속 순위와 법정상속분을 계산합니다. 유언·기여분·특별수익·대습상속은 반영하지 않은 참고용입니다.</p></div>
<form class="calc" id="inh" onsubmit="return false"><label>배우자<select name="sp"><option value="1">있음</option><option value="0">없음</option></select></label><label>자녀 수<input name="ch" type="number" min="0" max="10" value="2"></label><label>부모(생존) 수<input name="pa" type="number" min="0" max="2" value="0"></label><label>형제자매 수<input name="sb" type="number" min="0" max="10" value="0"></label></form>
<div class="out" id="inh-out"></div></div></section>
<script>(()=>{const f=document.getElementById('inh'),o=document.getElementById('inh-out');const g=(a,b)=>b?g(b,a%b):a;
const run=()=>{const sp=+f.sp.value,ch=+f.ch.value||0,pa=+f.pa.value||0,sb=+f.sb.value||0;let r=[],k;
if(ch)k=['자녀',ch];else if(pa)k=['부모',pa];else if(!sp&&sb)k=['형제자매',sb];
if(k){const sh=sp&&k[0]!=='형제자매'?3:0,tot=k[1]*2+sh;if(sh)r.push(['배우자',3,tot]);for(let i=1;i<=k[1];i++)r.push([k[0]+(k[1]>1?' '+i:''),2,tot]);}else if(sp)r.push(['배우자',1,1]);
const lab=k?(k[0]==='형제자매'?3:k[0]==='부모'?2:1)+'순위 상속':'배우자 단독 상속';
o.innerHTML=r.length?'<b>'+lab+'</b>'+r.map(([n,a,b])=>{const d=g(a,b);return'<p><span>'+n+'</span><i style="--w:'+(a/b*100)+'%"></i><em>'+a/d+'/'+b/d+' ('+(a/b*100).toFixed(1)+'%)</em></p>'}).join(''):'<p>입력한 상속인이 없습니다. 4촌 이내 방계혈족 여부를 상담으로 확인하세요.</p>';};
f.oninput=run;run();})();</script>""",
"admin": """<section class="g-tool" id="tool"><div class="wrap"><div class="g-sh"><small>TOOL</small><h2>불복 기한 계산기</h2><p>처분이 있음을 안 날을 넣으면 행정심판·행정소송 마감일을 계산합니다. 마지막 날이 토요일·공휴일이면 그다음 날까지이며, 개별 법률에 다른 기한이 있으면 그 기한이 먼저입니다.</p></div>
<form class="calc" id="dl" onsubmit="return false"><label>처분이 있음을 안 날<input name="d" type="date"></label></form>
<div class="out" id="dl-out"></div></div></section>
<script>(()=>{const f=document.getElementById('dl'),o=document.getElementById('dl-out');const t=new Date();f.d.value=t.toISOString().slice(0,10);
const run=()=>{if(!f.d.value)return;const d=new Date(f.d.value+'T00:00:00'),e=new Date(d);e.setDate(e.getDate()+90);const left=Math.ceil((e-new Date(new Date().toDateString()))/864e5);
const fmt=x=>x.getFullYear()+'. '+(x.getMonth()+1)+'. '+x.getDate()+'.';o.innerHTML='<b>마감일 '+fmt(e)+'</b><p><span>행정심판 청구</span><em>안 날부터 90일 → '+fmt(e)+'</em></p><p><span>행정소송 제기</span><em>안 날부터 90일 → '+fmt(e)+'</em></p><p class="'+(left<0?'over':'')+'"><span>남은 기간</span><em>'+(left<0?'기한이 지났습니다. 다른 다툼 방법을 상담으로 확인하세요.':left+'일')+'</em></p>';};
f.oninput=run;run();})();</script>""",
"civil": """<section class="g-tool" id="tool"><div class="wrap"><div class="g-sh"><small>CHECK</small><h2>소멸시효 한눈에 보기</h2><p>시효가 지나면 받을 돈이 있어도 청구할 수 없습니다. 대표적인 기간이며, 시효는 소송·가압류·승인 등으로 중단될 수 있습니다.</p></div>
<table class="tbl"><thead><tr><th>채권</th><th>기간</th><th>근거</th></tr></thead><tbody>
<tr><td>일반 민사채권 (대여금 등)</td><td>10년</td><td>민법 제162조</td></tr><tr><td>상행위로 생긴 채권</td><td>5년</td><td>상법 제64조</td></tr>
<tr><td>공사대금·의료비 등</td><td>3년</td><td>민법 제163조</td></tr><tr><td>숙박료·음식료 등</td><td>1년</td><td>민법 제164조</td></tr>
<tr><td>불법행위 손해배상</td><td>안 날부터 3년, 있은 날부터 10년</td><td>민법 제766조</td></tr><tr><td>판결로 확정된 채권</td><td>10년</td><td>민법 제165조</td></tr>
</tbody></table></div></section>""",
}

# 센터 페이지 = 메인(index.html) 템플릿 그대로: 같은 머리·히어로(사진+켄번스)·사진 카드·강점·상담 절차·배너·사례·후기·미디어·상담·오시는 길·푸터
ITIMG = {"corp-general": "s-boardroom", "intl-arbitration": "s-skyline", "mgmt-consulting": "n/meeting3", "fair-trade": "n/scale-coins",
         "restructuring-ma": "s-handshake", "finance-capital": "s-towers", "ai-data": "s-night-laptop", "ip": "s-writing", "ent-sports": "s-lecture",
         "healthcare": "s-sprout", "defense": "n/glass", "white-collar": "n/defense-seat", "criminal": "n/handcuff", "sex-crime": "n/court",
         "dui-traffic": "n/night-office", "drugs": "n/gavel", "special-task": "n/statue-gavel", "civil": "n/lawyer-doc", "construction-realestate": "n/property",
         "family": "n/couple", "divorce": "s-father", "inheritance": "n/estate-law", "admin-constitutional": "s-assembly", "tax-customs": "s-bills",
         "school-violence": "s-notebook", "foreigner": "n/panel", "labor-injury": "s-meeting", "serious-accident": "n/table"}
BANNER = {"corporate": "s-desk-city", "criminal": "s-court", "civil": "s-library", "family": "s-sprout", "admin": "s-round-lib", "labor": "s-desk-top"}
STORY = ["n/story-key", "n/story-arch", "n/story-hall", "n/story-stairs"]
def sect(html_, cls):  # 메인에서 섹션 하나 그대로
    a = html_.index(f'<section class="{cls}"'); return html_[a:html_.index("</section>", a) + 10]

STEPIMG = ["n/step-talk", "n/lawyer-desk", "n/court", "n/step-shake"]
AREA_OF = {"criminal": "형사", "civil": "민사", "family": "가사"}  # 상담 폼 분야 (app.py AREAS). 나머지 센터는 기타
PERSON = '<svg viewBox="0 0 48 48"><circle cx="22" cy="15" r="9"/><path d="M5 43c0-10 7-16 17-16s17 6 17 16z"/><circle class="ck" cx="37" cy="33" r="8"/><path class="cm" d="M33 33l3 3 5-6"/></svg>'
# 센터 페이지 스크립트: 단계 탭(5초마다 자동 넘김, 누르면 멈춤) · 사례 유형 필터 · 모든 분야 탭
GJS = """<script>(()=>{const $=(s,r)=>[...r.querySelectorAll(s)];
const st=document.querySelector('.g-stage');let n=0;const go=i=>{n=i;$('.tabs button',st).forEach((b,j)=>b.classList.toggle('on',j===i));$('.pane',st).forEach((p,j)=>p.classList.toggle('on',j===i))};
const auto=setInterval(()=>go((n+1)%4),5000);$('.tabs button',st).forEach((b,i)=>b.onclick=()=>{clearInterval(auto);go(i)});
const cs=document.getElementById('cases');$('.g-chips button',cs).forEach(b=>b.onclick=()=>{$('.g-chips button',cs).forEach(x=>x.classList.toggle('on',x===b));$('.case',cs).forEach(c=>c.hidden=!!b.dataset.t&&c.dataset.t!==b.dataset.t)});
const al=document.querySelector('.g-all');$('.gl button',al).forEach((b,i)=>b.onclick=()=>{$('.gl button',al).forEach(x=>x.classList.toggle('on',x===b));$('.gp',al).forEach((p,j)=>p.classList.toggle('on',j===i))});
})();</script>"""

def gpage(k):
    d = GROUPS_D[k]; gi = GKEY.index(k); en, gko, slugs = GROUPS[gi]
    items = slugs + EXTRA.get(k, [])
    nm = amp(d["center"]).replace("알엠 ", ""); name = amp(d["name"])
    arrow = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    tabs = "".join(f'<a href="../{x}/index.html"{" class=on" if x == k else ""}>{GROUPS_D[x]["name"]}</a>' for x in GKEY)
    h1 = "".join(f'<span class="ln"><span>{amp(x)}</span></span>' for x in d["hero"]["h1"].split("<br>"))
    dl = lambda i, n: " d1" if i % n == 1 else " d2" if i % n == 2 else ""
    S = d["steps"]["items"]
    stabs = "".join(f'<button type="button"{" class=on" if i == 0 else ""}><i>{i + 1:02d}</i>{amp(x["t"])}</button>' for i, x in enumerate(S))
    panes = "".join(f'<div class="pane{" on" if i == 0 else ""}"><div class="ph"><img src="img/{STEPIMG[i]}.webp" alt="" loading="lazy"></div><div class="tx"><small>STEP {i + 1:02d}</small><h3>{amp(x["t"])}</h3><p>{amp(x["p"])}</p><a class="pill dark arrow" href="#form">이 단계 상담하기</a></div></div>' for i, x in enumerate(S))
    ask = "".join(f'<details class="reveal{dl(i, 3)}" name="ask"><summary><svg viewBox="0 0 24 24"><path d="{AREAS[i][3]}"/></svg>{amp(x["q"])}</summary><p>{amp(x["a"])}</p></details>' for i, x in enumerate(d["ask"]["items"]))
    faq = "".join(f'<details class="reveal"><summary>{amp(q["q"])}</summary><p>{amp(q["a"])}</p></details>' for q in d["faq"])
    tags = list(dict.fromkeys(c["tag"] for c in d["cases"]))
    chips = '<button type="button" class="on" data-t="">전체</button>' + "".join(f'<button type="button" data-t="{amp(t)}">{amp(t)}</button>' for t in tags)
    cases = "".join(f'<a class="case reveal{dl(i, 2)}" data-t="{amp(c["tag"])}" href="#form"><div class="meta"><span class="area">{amp(c["tag"])}</span><time>예시</time></div><h3>{amp(c["title"])}</h3><p>{amp(c["summary"])}</p><div class="foot"><b>결과 · {amp(c["result"])}</b></div></a>' for i, c in enumerate(d["cases"]))
    cards = "".join(f'<a class="card bg reveal{dl(i, 3)}" href="practice-{x}.html"><img src="img/{ITIMG[x]}.webp" alt="" loading="lazy"><div class="t"><small>{i + 1:02d}</small><h3>{amp(FBY[x]["item"])}</h3><p>{amp(FBY[x]["h1sub"])}</p></div></a>' for i, x in enumerate(items))
    rv = lambda r: f'<article><div class="av">{PERSON}<span>★★★★★</span></div><div><em>{amp(r["tag"])}</em><h3>{amp(r["title"])}</h3><p>{amp(r["name"])} 의뢰인</p></div></article>'
    R1 = "".join(rv(r) for r in d["reviews"]); R2 = "".join(rv(r) for r in d["reviews"][2:] + d["reviews"][:2])
    allg = "".join(f'<button type="button"{" class=on" if x == k else ""}>{GROUPS_D[x]["name"]}{arrow}</button>' for x in GKEY)
    allp = "".join(f'<div class="gp{" on" if x == k else ""}">' + "".join(f'<a href="practice-{sl}.html">{amp(FBY[sl]["item"])}{arrow}</a>' for sl in GROUPS[i][2])
                   + f'<a class="ctr" href="{x}/index.html">{GROUPS_D[x]["name"]} 센터 바로가기{arrow}</a></div>' for i, x in enumerate(GKEY))
    trust = "".join(f'<li class="reveal{dl(i, 3)}"><div class="top"><span>알엠의 <b>3가지 약속</b></span><i>{n}</i></div><h3>{a}</h3><small>{b}</small><p>{c}</p></li>' for i, (n, a, b, c) in enumerate([
        ("Ⅰ", "대표변호사 직접 수행", "Direct Counsel", "상담부터 서면 작성, 법정 출석까지 사무장이 아닌 대표변호사가 맡습니다."),
        ("Ⅱ", "비용·범위 서면 안내", "Written Estimate", "수임 전에 예상 비용과 업무 범위를 글로 먼저 안내합니다."),
        ("Ⅲ", "단계마다 바로 보고", "Progress Report", "기일과 서면 제출 같은 주요 단계를 의뢰인께 바로 알려드립니다.")]))
    # 상단 메뉴 5개 + 올리면 펼쳐지는 하위 메뉴 (main.js 가 열 위치를 메뉴 글자에 맞춤)
    M = [("센터 소개", "#intro", [("센터 소개", "#intro"), ("단계별 대응", "#why"), ("알엠의 3가지 약속", "#trust"), ("오시는 길", "#location"), ("알엠 홈", "./")]),
         ("업무사례", "#cases", [(f"{name} 업무사례", "#cases"), ("의뢰인 후기", "#reviews"), ("상담 전 확인사항", "#ask"), ("전체 사례", "cases.html")]),
         ("업무분야", "#areas", [(amp(FBY[x]["item"]), f"practice-{x}.html") for x in items[:5]] + [("모든 분야 보기", "#all")]),
         ("대표변호사", "#attorney", [("변환봉 변호사", "#attorney"), ("주요 경력", "profile.html"), ("방송 · 미디어", "#media")]),
         ("소식·자료", "news.html", [("언론보도", "news.html?t=press"), ("공지사항", "news.html?t=notice"), ("법률정보", "news.html?t=column")])]
    menu = '<nav class="menu">' + "".join(f'<a href="{u}">{t}</a>' for t, u, _ in M) + '</nav>'
    mega = '<div class="wrap cols">' + "".join("<ul>" + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in sub) + "</ul>" for _, _, sub in M) + '</div>'
    allm = '<div class="wrap cols">' + "".join(f"<div><h3>{t}</h3><ul>" + "".join(f'<li><a href="{u}">{t2}</a></li>' for t2, u in sub) + "</ul></div>" for t, _, sub in M[:4]) + '</div>'
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": text(q["q"]), "acceptedAnswer": {"@type": "Answer", "text": text(q["a"])}} for q in d["faq"]]},
          {"@context": "https://schema.org", "@type": "LegalService", "name": "로펌 알엠 법률사무소 " + text(d["center"]), "telephone": "1644-7702",
           "address": {"@type": "PostalAddress", "streetAddress": "위례광장로 322, 212호", "addressLocality": "성남시 수정구", "addressRegion": "경기도", "addressCountry": "KR"}}]
    # 머리: 메인 그대로, 스플래시 빼고 제목·설명·로고·메뉴만 센터용
    h = P[:P.index("<main>")]
    h = re.sub(r'<!-- Splash.*?<header class="gnb">', '<header class="gnb">', h, flags=re.S)
    h = re.sub(r"<title>.*?</title>", lambda m: f"<title>{amp(d['title'])}</title>", h)
    h = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{amp(d["desc"])}">', h)
    h = h.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld) + "</head>")
    h = h.replace('<body class="final"', '<body class="final center-page"')
    h = h.replace('<span class="ko">로펌 알엠 법률사무소<small>LAW FIRM RM</small></span>', f'<span class="ko">로펌 알엠 {nm}<small>{d["en"]}</small></span>', 1)
    for pat, rep in [(r'<nav class="menu">.*?</nav>', menu), (r'<div class="wrap cols">.*?</div>', mega), (r'(<div id="allmenu".*?</button>\s*)<div class="wrap cols">.*?</div>\s*</div>', r'\1' + allm)]:
        h, n = re.subn(pat, lambda m, rep=rep: m.expand(rep) if "\\1" in rep else rep, h, count=1, flags=re.S)
        assert n == 1, pat
    t = P[P.index("</main>"):]
    t = re.sub(r"<script>\n// 메인: 최신 사례.*?</script>\n", "", t, flags=re.S)
    body = f"""<main>
  <section class="hero" id="about">
    <img class="bg" src="{GIMG[k]}" alt="">
    <div class="wrap">
      <p class="eb reveal">{amp(d["hero"]["eyebrow"])}</p>
      <h1>{h1}</h1>
      <p class="reveal d1">{amp(d["hero"]["sub"])}</p>
      <div class="cta reveal d2"><a href="#form" class="pill glow">온라인으로 상담을 신청해보세요 ↗</a><a href="tel:16447702" class="pill" style="background:transparent;color:#fff;border-color:rgba(255,255,255,.7)">전화 상담 1644-7702</a></div>
    </div>
  </section>
  <nav class="g-tabs"><div class="wrap"><span>센터 바로 이동</span>{tabs}</div></nav>

  <section class="b-intro" id="intro">
    <div class="wrap">
      <h2 class="reveal">로펌 알엠 {nm}<small>{d["en"]}</small></h2>
      <p class="sub reveal d1">{amp(d["intro"]["h2"])}</p>
      <p class="lead reveal d2">{amp(d["intro"]["p"])}</p>
    </div>
  </section>

  <section class="g-stage" id="why"><div class="wrap">
    <div class="g-h reveal"><p>단계별 체계적 대응</p><h2>{amp(d["steps"]["h2"])}</h2></div>
    <div class="tabs reveal">{stabs}</div>
    <div class="panes reveal">{panes}</div>
  </div></section>

  <section class="g-ask2" id="ask"><div class="wrap">
    <div class="g-h c reveal"><h2>{amp(d["ask"]["h2"])}</h2><p>많은 분들이 상담에서 묻는 질문을 대표변호사가 미리 답합니다</p></div>
    <div class="boxes">{ask}</div>
    <div class="f-main faq2"><h3 class="reveal">{name} 자주 묻는 질문</h3>{faq}</div>
  </div></section>

  <section class="sec cases-home" id="cases">
    <div class="wrap">
      <div class="sec-head reveal"><div class="row"><div><h2>{name} 업무사례</h2><p>사건 유형별 진행 사례 (예시 문구)</p></div><a class="pill sm arrow" href="cases.html">사례 더보기</a></div></div>
      <div class="g-chips reveal">{chips}</div>
      <div class="cases">{cases}</div>
    </div>
  </section>

  <section class="c-bento g-bento" id="areas"><div class="wrap">
    <div class="g-h reveal"><p>유형에 따라 대응 전략은 달라집니다</p><h2>{name} 세부 대응분야</h2></div>
    <div class="grid n{len(items)}">{cards}</div>
  </div></section>

  <section class="g-atty" id="attorney"><div class="wrap">
    <div class="ph reveal"><img src="img/attorney.webp" alt="변환봉 대표변호사" loading="lazy"></div>
    <div class="tx reveal d1"><p>당신 곁을 지킬 한 사람</p><h2>대표변호사 <b>변환봉</b></h2>
      <ul><li>사법시험 합격 · 사법연수원 수료</li><li>연세대학교 법학과</li><li>前 서울지방변호사회 사무총장</li><li>前 서강대 · 아주대 법학전문대학원 출강</li><li>코스피 · 코스닥 상장기업 법률자문 및 M&amp;A 다수 수행</li><li>특검 사건 다수 변호 · 노사관계 분쟁 자문</li><li>MBC 100분토론 · TV조선 · 채널A · MBN 출연</li></ul>
      <a class="pill dark arrow" href="profile.html">약력 전체 보기</a></div>
  </div></section>

  <section class="g-mq" id="reviews">
    <div class="wrap g-h reveal"><p>일상을 되찾은 의뢰인들과 함께한</p><h2>{nm} 의뢰인 후기</h2><span>직접 상담하고 진행한 분들의 말 (예시 문구)</span></div>
    <div class="row"><div class="track">{R1}{R1}{R1}{R1}</div></div>
    <div class="row rev"><div class="track">{R2}{R2}{R2}{R2}</div></div>
  </section>

  <section class="g-form" id="form"><img class="bgi" src="img/{BANNER[k]}.webp" alt="" loading="lazy"><div class="wrap"><div class="box reveal">
    <div class="l"><h2>{nm}<br>상담 접수</h2><p>남겨주신 내용은 대표변호사가<br>직접 확인하고 연락드립니다.</p>
      <div class="btns"><a href="tel:16447702">전화 상담 <b>1644-7702</b></a><a class="kakao" href="#">카카오톡 상담</a></div></div>
    <form class="cform" id="cform">
      <input type="hidden" name="utm_source"><input type="hidden" name="utm_medium"><input type="hidden" name="utm_campaign"><input type="hidden" name="utm_term">
      <input type="hidden" name="landing_url"><input type="hidden" name="referrer"><input type="hidden" name="area" value="{AREA_OF.get(k, "기타")}">
      <input name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px">
      <div class="two"><div class="row"><label for="f-name">성함</label><input id="f-name" name="name" required maxlength="30"></div>
        <div class="row"><label for="f-phone">연락처</label><input id="f-phone" name="phone" type="tel" required pattern="[0-9\\-]{{9,13}}" placeholder="010-0000-0000"></div></div>
      <div class="row"><label for="f-msg">문의 내용</label><textarea id="f-msg" name="message" maxlength="2000" placeholder="[{name}] 사건 개요를 간단히 적어주세요."></textarea></div>
      <label class="agree"><input type="checkbox" name="agree" required> 개인정보 수집·이용(상담 목적, 1년 보관)에 동의합니다.</label>
      <button class="pill arrow" type="submit">온라인 상담 문의</button>
      <p class="msg" role="status"></p>
    </form>
  </div></div></section>

  {TOOLS.get(k, "")}

  <section class="g-all" id="all"><div class="wrap"><div class="box reveal">
    <div class="gl"><h2>모든 분야<small>한눈에 보기</small></h2>{allg}</div>
    <div class="gr">{allp}</div>
  </div></div></section>

  <section class="g-trust" id="trust"><img src="img/n/night-office.webp" alt="" loading="lazy"><div class="wrap"><ul>{trust}</ul></div></section>

  {sect(P, "sec media")}

  <section class="g-quick"><div class="wrap">
    <h2 class="reveal">{name} 사건, 더 궁금한 점이 있으신가요?</h2>
    <div class="grid">
      <a class="reveal" href="#form"><b>상담 신청</b><p>전화 1644-7702<br>24시간 상담 접수</p>{arrow}</a>
      <a class="reveal d1" href="#cases"><b>업무사례</b><p>사건 유형별<br>진행 사례</p>{arrow}</a>
      <a class="reveal d2" href="#attorney"><b>변호사 소개</b><p>수사와 재판을 직접 맡는<br>대표변호사</p>{arrow}</a>
      <a class="reveal d3" href="#reviews"><b>의뢰인 후기</b><p>직접 진행한<br>분들의 이야기</p>{arrow}</a>
    </div>
  </div></section>

  {sect(P, "sec apply loc")}
{GJS}
"""
    os.makedirs(os.path.join(R, k), exist_ok=True)
    open(os.path.join(R, k, "index.html"), "w", encoding="utf-8").write(to_root(h + body + t))

for k in GKEY: gpage(k)
print("built center pages", len(GKEY))

