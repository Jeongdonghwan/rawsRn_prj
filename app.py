import csv
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
DATA = Path(__file__).with_name("consults.csv")
AREAS = {"형사", "민사", "개인회생", "가사", "기타"}
HUB_URL = os.getenv("HUB_URL", "").rstrip("/")       # 통합 상담 어드민 주소 (예: http://localhost:5100)
SITE_SECRET = os.getenv("SITE_SECRET", "")           # 어드민 > 사이트 설정에서 발급한 비밀키
log = logging.getLogger("consult")


@app.get("/")
def index():
    return app.send_static_file("index.html")


def save_csv(row: list[str]) -> None:
    """허브 전송과 무관하게 항상 남기는 로컬 백업."""
    new = not DATA.exists()
    with DATA.open("a", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        if new:
            w.writerow(["접수일시", "성함", "연락처", "분야", "내용", "허브전송"])
        # 엑셀 수식 주입 방지
        w.writerow([("'" + v if v[:1] in "=+-@" else v) for v in row])


def send_to_hub(payload: dict) -> int | None:
    """어드민 접수 API로 서버→서버 전송. 실패해도 예외를 내지 않고 None."""
    if not (HUB_URL and SITE_SECRET):
        return None
    try:
        r = requests.post(f"{HUB_URL}/api/v1/inquiries", json=payload, headers={"X-Site-Key": SITE_SECRET}, timeout=5)
        if r.status_code == 201:
            return r.json().get("id")
        log.warning("hub rejected %s %s", r.status_code, r.text[:200])
    except requests.RequestException as e:
        log.warning("hub unreachable: %s", e)
    return None


@app.post("/api/consult")
def consult():
    f = request.form
    name = f.get("name", "").strip()[:30]
    phone = f.get("phone", "").strip()
    area = f.get("area", "")
    message = f.get("message", "").strip()[:2000]
    if not name or not re.fullmatch(r"[0-9\-]{9,13}", phone) or area not in AREAS or not f.get("agree"):
        return jsonify(error="입력값을 확인해 주세요"), 400
    if f.get("website"):  # 허니팟: 봇에게는 성공처럼 보이게
        return jsonify(ok=True)

    hub_id = send_to_hub({
        "name": name, "phone": phone, "privacy_agreed": True, "inquiry_type": area, "message": message,
        "utm_source": f.get("utm_source", ""), "utm_medium": f.get("utm_medium", ""),
        "utm_campaign": f.get("utm_campaign", ""), "utm_term": f.get("utm_term", ""),
        "referrer": f.get("referrer", ""), "landing_url": f.get("landing_url", ""),
        "client_ua": request.user_agent.string[:300],
    })
    save_csv([datetime.now().isoformat(" ", "seconds"), name, phone, area, message, str(hub_id or "")])
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True, port=5055)
