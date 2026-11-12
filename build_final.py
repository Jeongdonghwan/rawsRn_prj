"""최종안 static/final.html 조립: b.html 기반 + c.html 블록. 실행: python build_final.py (build_pages.py 다음에)"""
import re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
rd = lambda f: open(os.path.join(R, f), encoding="utf-8").read()
B, C = rd("b.html"), rd("c.html")

def sec(src, key, tag="section"):
    m = re.search(rf'<{tag}[^>]*(?:id="{key}"|class="{key}[" ])[^>]*>.*?</{tag}>', src, re.S)
    assert m, key
    return m.group(0)

P = B
# 1. 인트로 큰 사진 → C 벤토 그리드
intro = sec(B, "intro")
grid = re.search(r'(      <div class="grid">.*?\n      </div>)\n    </div>\n  </section>', sec(C, "attorney"), re.S).group(1)
intro2 = re.sub(r'      <div class="big reveal d2">.*?    </div>\n  </section>',
                '    </div>\n  </section>\n\n  <section class="c-bento"><div class="wrap">\n' + grid.replace("\\", "\\\\") + '\n  </div></section>', intro, flags=re.S)
assert intro2 != intro
P = P.replace(intro, intro2)

# 2. 수치 4칸 → 경쟁력 8칸 표 (01~06 경쟁력 + 07 24시간 + 08 4개 분야)
edge = sec(B, "edge")
rows = re.findall(r'<div class="pic"><img src="([^"]+)"[^>]*></div>\s*<div><div class="n">(\d+)</div><h3>(.*?)</h3><p>(.*?)</p>', edge, re.S)
assert len(rows) == 6, rows
rows += [("img/s-consult.webp", "07", "24시간 상담 접수", "밤낮 없이 접수하면 확인 즉시 연락드립니다. 주말은 예약제로 운영합니다."),
         ("img/s-justice.webp", "08", "형사 · 민사 · 개인회생 · 가사", "개인 의뢰인이 마주하는 네 분야를 대표변호사가 처음부터 끝까지 직접 대응합니다.")]
feat = '''  <section class="b-feat" id="edge">
    <div class="wrap">
      <h2 class="reveal">알엠의 경쟁력</h2>
      <ul>
''' + "".join(f'        <li class="reveal{" d" + str(i % 4) if i % 4 else ""}"><div class="pic"><img src="{s}" alt="" loading="lazy"></div><div class="n">{n}</div><h3>{h}</h3><p>{p}</p></li>\n' for i, (s, n, h, p) in enumerate(rows)) + '''      </ul>
    </div>
  </section>'''
P = P.replace(sec(B, "b-stats"), feat)

# 4. 경쟁력 교차 섹션 삭제 (탭 #edge 는 8칸 표로 연결됨)
P = re.sub(r"  <!-- 경쟁력[^\n]*\n  " + re.escape(edge) + r"\n+", "", P)
assert edge not in P

# 5. 남색 띠 → 상담 절차 + 인용 2단 + 최근 업무사례 슬라이더
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
rail = sec(C, "cases").replace('id="cases"', 'id="recent"')
assert "  <!-- 철학 (다크 밴드) -->\n  " + sec(B, "phil") in P
P = P.replace("  <!-- 철학 (다크 밴드) -->\n  " + sec(B, "phil"),
              "  <!-- 상담 절차 -->\n" + steps + "\n\n  <!-- 철학 -->\n" + quote + "\n\n  <!-- 최근 업무사례 슬라이더 -->\n" + rail)

# 6. 의뢰인 이야기 (practice 와 clients 사이)
rev = sec(C, "media").replace('id="media"', 'id="reviews"')
rev = rev.replace("<b>당일 상담 예약</b><p>평일 오전 접수 시 당일 상담, 주말·야간 예약제.</p>", "<b>24시간 상담 접수</b><p>밤낮 없이 접수, 주말은 예약제.</p>")
assert "24시간 상담 접수</b>" in rev
P = P.replace("  <!-- CLIENTS -->", "  <!-- 의뢰인 이야기 -->\n" + rev + "\n\n  <!-- CLIENTS -->")

# 7. 갤러리 (clients 와 cases 사이)
gal = sec(C, "news").replace('id="news"', 'id="gallery"')
P = P.replace("  <!-- CASES -->", "  <!-- 갤러리 -->\n" + gal + "\n\n  <!-- CASES -->")

# 머리·스크립트
P = P.replace('<link rel="stylesheet" href="css/b.css">', '<link rel="stylesheet" href="css/b.css">\n<link rel="stylesheet" href="css/c.css">\n<link rel="stylesheet" href="css/final.css">')
P = re.sub(r"<title>.*?</title>", "<title>로펌 알엠 법률사무소 | 최종안</title>", P)
P = P.replace("<body>", '<body class="final">', 1)
cscript = re.search(r"<script>\n// C: 업무사례 가로 슬라이더.*?</script>", C, re.S).group(0).replace("<script>\n", "<script>\n{\n").replace("\n</script>", "\n}\n</script>")
P = P.replace('<script src="js/main.js"></script>', cscript + '\n<script src="js/main.js"></script>')

ids = re.findall(r' id="([^"]+)"', P)
dup = {i for i in ids if ids.count(i) > 1}
assert not dup, dup
open(os.path.join(R, "final.html"), "w", encoding="utf-8").write(P)
print("built final.html", len(P))
