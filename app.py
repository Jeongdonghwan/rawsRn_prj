import csv
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="")
DATA = Path(__file__).with_name("consults.csv")
AREAS = {"형사", "민사", "개인회생", "가사", "기타"}


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/consult")
def consult():
    f = request.form
    name = f.get("name", "").strip()[:30]
    phone = f.get("phone", "").strip()
    area = f.get("area", "")
    message = f.get("message", "").strip()[:2000]
    if not name or not re.fullmatch(r"[0-9\-]{9,13}", phone) or area not in AREAS or not f.get("agree"):
        return jsonify(error="입력값을 확인해 주세요"), 400
    # ponytail: CSV 저장만. 알림이 필요하면 여기서 메일/카카오 알림톡 발송 추가
    new = not DATA.exists()
    with DATA.open("a", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        if new:
            w.writerow(["접수일시", "성함", "연락처", "분야", "내용"])
        # 엑셀 수식 주입 방지
        w.writerow([datetime.now().isoformat(" ", "seconds")] + [("'" + v if v[:1] in "=+-@" else v) for v in (name, phone, area, message)])
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True, port=5055)
