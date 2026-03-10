# 使用說明（Skyscanner 便宜機票搜尋工具）

本工具提供兩種使用方式：

1. **Web 介面**（推薦）
2. **Python API**（進階）

---

## 1) Web 介面快速開始

### 啟動

```bash
python web_app.py
```

打開瀏覽器：<http://localhost:8000>

### 操作步驟

1. 輸入 **段數**（1 到 4 段）。
2. 輸入 **最多輸出連結數**（建議 20~200）。
3. 依段數填寫各段欄位：
   - 出發機場（可多個，逗號分隔）
   - 抵達機場（可多個，逗號分隔）
   - 出發起日 / 出發迄日
   - 必經機場（可留白）
   - 可出關停留（勾選表示可接受）
4. 點擊「**產生搜尋連結**」。
5. 在結果區點擊連結，於新分頁開啟 Skyscanner。

### 欄位範例

- 出發機場：`TPE,KHH`
- 抵達機場：`NRT,HND`
- 必經機場：`SIN`
- 日期：`2026-06-01` ~ `2026-06-03`

---

## 2) Python API 使用

```python
from datetime import date
from flight_search import SearchConfig, SegmentPreference, generate_queries

config = SearchConfig(
    segments=[
        SegmentPreference(
            origins=["TPE", "KHH"],
            destinations=["LHR", "LGW"],
            depart_from=date(2026, 3, 1),
            depart_to=date(2026, 3, 3),
            via_airports=["SIN"],
            allow_exit_transit=True,
        )
    ],
    max_queries=50,
)

for q in generate_queries(config):
    print(q.to_skyscanner_url())
```

---

## 注意事項

- 多段上限為 **4 段**。
- 日期範圍越大、機場選項越多，組合數會快速增加。
- `via_airports` 與 `allow_exit_transit` 為搜尋偏好輔助資訊，仍建議在 Skyscanner 結果頁人工再確認。
