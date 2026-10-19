const KAKAO_URL = '#'; // TODO: 카카오채널 URL (http://pf.kakao.com/_xxxx)
document.querySelectorAll('.kakao').forEach(a => { a.href = KAKAO_URL; if (KAKAO_URL !== '#') a.target = '_blank'; });
document.querySelector('.totop')?.addEventListener('click', e => { e.preventDefault(); scrollTo({ top: 0, behavior: 'smooth' }); });

// ---------- Splash ----------
const splash = document.getElementById('splash');
const ready = () => document.body.classList.add('ready');
if (splash) { // ponytail: 매 진입마다 재생. 세션당 1회로 바꾸려면 sessionStorage 체크 추가
  splash.hidden = false;
  document.body.classList.add('lock');
  splash.querySelector('.name').innerHTML = [...'법률사무소 알엠']
    .map((c, i) => `<span style="animation-delay:${0.9 + i * 0.07}s">${c === ' ' ? '&nbsp;' : c}</span>`).join('');
  let closed = false;
  const close = () => {
    if (closed) return;
    closed = true;
    splash.classList.add('done');
    document.body.classList.remove('lock');
    setTimeout(ready, 300);
    setTimeout(() => splash.remove(), 1100);
  };
  splash.querySelector('.skip').onclick = close;
  setTimeout(close, 2800);
} else {
  splash?.remove();
  ready();
}

// ---------- Header ----------
const gnb = document.querySelector('header.gnb');
const onScroll = () => gnb.classList.toggle('solid', scrollY > 40);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

// ---------- 상단 메뉴 드롭다운 (마우스 오버) ----------
if (gnb.querySelector('.mega')) {
  const setOpen = v => { gnb.classList.toggle('open', v); gnb.querySelector('.mega').setAttribute('aria-hidden', !v); };
  // 각 하위 메뉴 열을 상단 메뉴 글자 x 위치에 맞춤
  const align = () => {
    const base = gnb.querySelector('.mega .cols').getBoundingClientRect().left;
    const links = gnb.querySelectorAll('nav.menu a');
    gnb.querySelectorAll('.mega .cols ul').forEach((ul, i) => { ul.style.left = (links[i].getBoundingClientRect().left - base) + 'px'; });
  };
  align(); addEventListener('resize', align);
  gnb.querySelector('nav.menu').addEventListener('mouseenter', () => { align(); setOpen(true); });
  gnb.addEventListener('mouseleave', () => setOpen(false));
  gnb.querySelectorAll('nav.menu a, .mega a').forEach(a => a.addEventListener('click', () => setOpen(false)));
}

// ---------- 전체메뉴 ----------
const allmenu = document.getElementById('allmenu');
if (allmenu) {
  const toggle = open => { allmenu.classList.toggle('open', open); allmenu.setAttribute('aria-hidden', !open); document.body.classList.toggle('lock', open); };
  document.querySelector('.burger').onclick = () => toggle(true);
  allmenu.querySelector('.close').onclick = () => toggle(false);
  allmenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => toggle(false)));
  addEventListener('keydown', e => e.key === 'Escape' && toggle(false));
}

// ---------- 스크롤 등장 ----------
const io = new IntersectionObserver(entries => entries.forEach(e => {
  if (!e.isIntersecting) return;
  e.target.classList.add('in');
  io.unobserve(e.target);
}), { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// ---------- 상담 신청 ----------
const form = document.getElementById('cform');
if (form) {
  // 유입 정보: URL의 utm 파라미터 + 랜딩 URL + 리퍼러 (상담 허브 통계용)
  const q = new URLSearchParams(location.search);
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term'].forEach(k => form.elements[k].value = q.get(k) || '');
  form.elements.landing_url.value = location.href;
  form.elements.referrer.value = document.referrer;
}
if (form) form.addEventListener('submit', async e => {
  e.preventDefault();
  const msg = form.querySelector('.msg'), btn = form.querySelector('button');
  btn.disabled = true;
  msg.textContent = '접수 중입니다…';
  try {
    const r = await fetch('/api/consult', { method: 'POST', body: new FormData(form) });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || '접수 실패');
    form.reset();
    msg.textContent = '상담 신청이 접수되었습니다. 빠르게 연락드리겠습니다.';
  } catch (err) {
    msg.textContent = err.message + ' — 전화(031-000-0000)로 문의해 주세요.';
  } finally {
    btn.disabled = false;
  }
});
