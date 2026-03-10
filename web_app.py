from __future__ import annotations

from datetime import date
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from flight_search import SearchConfig, SegmentPreference, generate_queries


def _csv_codes(text: str) -> list[str]:
    return [x.strip().upper() for x in text.split(",") if x.strip()]


def _parse_bool(text: str) -> bool:
    return text.lower() in {"1", "true", "yes", "on"}


def _build_segments(form: dict[str, list[str]], segment_count: int) -> list[SegmentPreference]:
    segments: list[SegmentPreference] = []
    for i in range(1, segment_count + 1):
        origins = _csv_codes(form.get(f"origins_{i}", [""])[0])
        destinations = _csv_codes(form.get(f"destinations_{i}", [""])[0])
        depart_from = date.fromisoformat(form.get(f"depart_from_{i}", [""])[0])
        depart_to = date.fromisoformat(form.get(f"depart_to_{i}", [""])[0])
        via_airports = _csv_codes(form.get(f"via_{i}", [""])[0])
        allow_exit_transit = _parse_bool(form.get(f"allow_exit_{i}", ["0"])[0])
        segments.append(
            SegmentPreference(
                origins=origins,
                destinations=destinations,
                depart_from=depart_from,
                depart_to=depart_to,
                via_airports=via_airports,
                allow_exit_transit=allow_exit_transit,
            )
        )
    return segments


def render_form(message: str = "", results: list[str] | None = None) -> str:
    result_html = ""
    if results:
        items = "".join(f'<li><a href="{escape(u)}" target="_blank">{escape(u)}</a></li>' for u in results)
        result_html = f"<h2>搜尋連結</h2><ol>{items}</ol>"

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <title>Skyscanner 便宜機票搜尋工具</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; max-width: 900px; }}
    fieldset {{ margin-bottom: 16px; }}
    label {{ display: block; margin: 6px 0; }}
    .msg {{ color: #b00020; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Skyscanner 便宜機票搜尋工具</h1>
  <p>支援多機場、日期範圍、多段（最多4段）、每段必經機場、可否出關停留。</p>
  <p class="msg">{escape(message)}</p>
  <form method="post" action="/search">
    <label>段數 (1-4)：<input type="number" name="segment_count" min="1" max="4" value="1" required></label>
    <label>最多輸出連結數：<input type="number" name="max_queries" min="1" value="50" required></label>
    <p>請先填「段數」，並填寫對應段位欄位（segment_1 ~ segment_4）。未使用段位可留白。</p>
    {''.join(_segment_fieldset(i) for i in range(1, 5))}
    <button type="submit">產生搜尋連結</button>
  </form>
  {result_html}
</body>
</html>
"""


def _segment_fieldset(i: int) -> str:
    return f"""
    <fieldset>
      <legend>segment_{i}</legend>
      <label>出發機場(可多選，逗號分隔): <input name="origins_{i}" placeholder="TPE,KHH"></label>
      <label>抵達機場(可多選，逗號分隔): <input name="destinations_{i}" placeholder="NRT,HND"></label>
      <label>出發起日(YYYY-MM-DD): <input name="depart_from_{i}" type="date"></label>
      <label>出發迄日(YYYY-MM-DD): <input name="depart_to_{i}" type="date"></label>
      <label>必經機場(可多個，逗號分隔): <input name="via_{i}" placeholder="SIN,HKG"></label>
      <label>可出關停留: <input name="allow_exit_{i}" type="checkbox" value="1"></label>
    </fieldset>
    """


class FlightSearchHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        self._send_html(render_form())

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/search":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)

        try:
            segment_count = int(form.get("segment_count", ["1"])[0])
            if segment_count < 1 or segment_count > 4:
                raise ValueError("段數必須介於 1 到 4")

            max_queries = int(form.get("max_queries", ["50"])[0])
            segments = _build_segments(form, segment_count)
            config = SearchConfig(segments=segments, max_queries=max_queries)
            urls = [q.to_skyscanner_url() for q in generate_queries(config)]
            self._send_html(render_form(f"成功產生 {len(urls)} 筆連結", urls))
        except Exception as exc:  # user input validation
            self._send_html(render_form(f"輸入錯誤：{exc}"))

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), FlightSearchHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
