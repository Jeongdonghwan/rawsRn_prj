"""최종안 static/final.html + consult.html + profile.html 조립: b.html 기반 + c.html 블록.
실행: python build_final.py (build_pages.py 다음에)"""
import re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
rd = lambda f: open(os.path.join(R, f), encoding="utf-8").read()
wr = lambda f, s: open(os.path.join(R, f), "w", encoding="utf-8").write(s)
B, C, T = rd("b.html"), rd("c.html"), rd("cases.html")

def sec(src, key, tag="section"):
    m = re.search(rf'<{tag}[^>]*(?:id="{key}"|class="{key}[" ])[^>]*>.*?</{tag}>', src, re.S)
    assert m, key
    return m.group(0)

def cut(src, comment, block):  # "  <!-- 주석 -->\n  <section>" 통째로 제거
    out = re.sub(r"  <!-- " + comment + r"[^\n]*\n  " + re.escape(block) + r"\n+", "", src)
    assert out != src, comment
    return out

P = B
# 1. 인트로 큰 사진 → 분야 벤토 (형사·민사·가사 한 줄씩 + 행정·노무 반반)
intro = sec(B, "intro")
grid = re.search(r'(      <div class="grid">.*?\n      </div>)\n    </div>\n  </section>', sec(C, "attorney"), re.S).group(1)
big = re.search(r'        <a class="big.*?</a>\n', grid, re.S).group(0)
cards = re.findall(r'        <div class="card reveal.*?\n        </div>\n', grid, re.S)
assert len(cards) == 4, len(cards)
row = lambda c: re.sub(r'class="card reveal[^"]*"', 'class="card row reveal"', c)
def card(cls, h3, p, pic, more, thumbs):
    th = "".join(f'              <a href="{more}"><span><img src="img/{s}-sm.webp" alt="" loading="lazy"></span>{a}<b>{b}</b></a>\n' for s, a, b in thumbs)
    return f'''        <div class="card {cls}">
          <div class="pic"><img src="img/{pic}.webp" alt="" loading="lazy"></div>
          <div class="body"><h3>{h3}</h3><p>{p}</p><a class="more" href="{more}">{h3} 전체 보기</a>
            <div class="thumbs">
{th}            </div>
          </div>
        </div>
'''
newgrid = ('      <div class="grid">\n' + big + row(cards[0]) + row(cards[1]) + row(cards[3])
           + card("reveal", "행정", "영업정지·면허취소 같은 처분에 대한 행정심판과 행정소송. 인허가와 과징금 대응까지.", "s-towers", "practice.html",
                  [("s-hall", "영업정지·면허취소", "처분 취소"), ("s-lawbooks", "집행정지·심판 청구", "행정심판"), ("s-desk-city", "인허가·과징금", "행정소송")])
           + card("reveal d1", "노무", "부당해고·임금체불·산재. 노사관계 분쟁 자문 경험으로 근로자와 사업주 양쪽을 압니다.", "s-meeting", "practice.html",
                  [("s-handshake", "구제신청·소송", "부당해고"), ("s-bills", "임금·퇴직금", "체불 청구"), ("s-writing", "징계·산재", "노사 분쟁")])
           + '      </div>')
intro2 = re.sub(r'      <div class="big reveal d2">.*?    </div>\n  </section>',
                '    </div>\n  </section>\n\n  <section class="c-bento"><div class="wrap">\n' + newgrid.replace("\\", "\\\\") + '\n  </div></section>', intro, flags=re.S)
assert intro2 != intro
P = P.replace(intro, intro2)

# 2·4. 수치 4칸, 경쟁력 교차 섹션 삭제
P = P.replace(sec(B, "b-stats"), "")
P = cut(P, "경쟁력", sec(B, "edge"))

# 3. 탭: 경쟁력·발자취 빼고 약력 페이지 링크
P = re.sub(r'(<nav class="b-tabs"[^>]*>\s*<div class="wrap">)\s*<a .*?</a>(\s*</div>)',
           r'\1<a href="#attorney" class="on">대표변호사 인사말</a><a href="#about2">알엠 소개</a><a href="profile.html">대표변호사 약력</a><a href="#practice">업무분야</a><a href="#location">오시는 길</a>\2', P, flags=re.S)
assert "알엠의 경쟁력" not in P

# 인사말: 약력표 → 별도 페이지 링크
greet = sec(B, "attorney")
career = re.search(r'          <ul class="career">.*?</ul>\n', greet, re.S).group(0)
P = P.replace(career, '          <p><a class="pill sm arrow" href="profile.html">대표변호사 약력 보기</a></p>\n')

# 5. 남색 띠 → 인용 2단 + 상담 절차 (슬라이더 없음)
steps = sec(C, "practice").replace('id="practice"', 'id="steps"')
quote = '''  <section class="b-quote" id="phil">
    <div class="wrap">
      <div class="cols">
        <blockquote class="reveal"><h3>직접 듣고, 직접 변론한다</h3><p>로펌 알엠 법률사무소의 첫 번째 원칙입니다. 의뢰인의 사정을 가장 잘 아는 사람이 법정에 서야 합니다. 상담부터 변론까지 담당이 바뀌지 않습니다.</p></blockquote>
        <blockquote class="reveal d1"><h3>결과 이후의 일상까지</h3><p>판결문은 끝이 아니라 시작입니다. 민사는 회수까지, 개인회생은 면책까지, 가사는 자녀의 내일까지. 결과 이후의 삶을 먼저 생각합니다.</p></blockquote>
      </div>
      <div class="mark reveal"><span class="mk">R<i>M</i></span><p><b>로펌 알엠 법률사무소</b>Reliable &amp; Meticulous — 믿을 수 있고, 꼼꼼하게. 의뢰인이 가장 힘든 순간에 곁에 있는 법률사무소가 되겠다는 뜻을 담았습니다.</p></div>
    </div>
  </section>'''
phil = "  <!-- 철학 (다크 밴드) -->\n  " + sec(B, "phil")
assert phil in P
P = P.replace(phil, "  <!-- 철학 -->\n" + quote + "\n\n  <!-- 상담 절차 -->\n" + steps)

# 발자취 → profile.html 로 이동
P = cut(P, "발자취", sec(B, "history"))

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
P = P.replace('<h2 class="en">CONSULTING</h2>', '<h2>상담 문의</h2>').replace('<h3>온라인 문의</h3>', '<h3>상담신청</h3>')

# 상담 신청 폼 → consult.html, 메인은 오시는 길만 가로로 길게
apply = sec(B, "apply")
form = re.search(r'      <div class="reveal">\n        <h2>온라인 상담 신청</h2>.*?</form>\n      </div>\n', apply, re.S).group(0)
loc = apply.replace(form, "").replace('<section class="sec apply" id="apply">', '<section class="sec apply loc" id="visit">').replace('<div class="wrap inner">', '<div class="wrap">')
P = P.replace(apply, loc)

# 푸터 링크 묶음 삭제
P = re.sub(r'    <div class="top">.*?\n    </div>\n', "", P, flags=re.S)

# 링크: 상담신청 → consult.html, 대표변호사 메뉴 → profile.html
P = P.replace('href="#apply"', 'href="consult.html"').replace('href="#attorney">대표변호사</a>', 'href="profile.html">대표변호사</a>').replace('href="#attorney">주요 경력', 'href="profile.html">주요 경력')
P = P.replace("btabs.map(a => document.querySelector(", "btabs.filter(a => a.getAttribute('href').startsWith('#')).map(a => document.querySelector(")

# 머리·스크립트
P = P.replace('<link rel="stylesheet" href="css/b.css">', '<link rel="stylesheet" href="css/b.css">\n<link rel="stylesheet" href="css/c.css">\n<link rel="stylesheet" href="css/final.css">')
P = re.sub(r"<title>.*?</title>", "<title>로펌 알엠 법률사무소 | 최종안</title>", P)
P = P.replace("<body>", '<body class="final">', 1)
rails = '''<script>
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
wr("final.html", P)
print("built final.html", len(P))

# ---- 서브 페이지 (cases.html 틀) ----
head = T[:T.index('<section class="sub-hero">')]
foot = T[T.index('<footer>'):]
for a, b in [('href="./#apply"', 'href="consult.html"'), ('href="./#attorney">대표변호사', 'href="profile.html">대표변호사'), ('href="./#attorney">주요 경력', 'href="profile.html">주요 경력'), ('href="./#consult"', 'href="consult.html"')]:
    head, foot = head.replace(a, b), foot.replace(a, b)
foot = re.sub(r'    <div class="top">.*?\n    </div>\n', "", foot, flags=re.S)
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

pg = greet.replace(career, "").replace(re.search(r'      <div class="wide reveal">.*?</div>\n      </div>\n', greet, re.S).group(0), "")
pg = pg.replace('<section class="b-greet" id="attorney">', '<section class="b-greet" id="attorney" style="padding-top:40px">')
sub("profile.html", "대표변호사", "로펌 알엠 법률사무소 대표변호사 변환봉 약력. 사법시험 합격, 前 서울지방변호사회 사무총장, 로스쿨 출강, 상장기업 법률자문, 특검 사건 변호.",
    "PROFILE", "대표변호사 변환봉", "사법시험을 거쳐 변호사가 된 뒤 서울지방변호사회 사무총장, 로스쿨 출강, 상장기업 법률자문과 특검 사건 변호를 두루 경험했습니다.",
    pg + "\n\n" + sec(B, "history"), css='\n<link rel="stylesheet" href="css/b.css">')
