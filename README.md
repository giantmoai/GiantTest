# GiantTest

這個工具可協助你在 Skyscanner 規劃「便宜機票」搜尋條件，支援：

- 自選機場（每段可多選出發/抵達機場）
- 時間範圍（每段可設出發日期區間）
- 多段行程（最多四段）
- 每段必經機場（`via_airports`）
- 中間機場是否可出關停留（`allow_exit_transit`）

## Web 介面

```bash
python web_app.py
```

啟動後打開 `http://localhost:8000`。

### 畫面說明

Web 首頁分成三塊：

1. **畫面說明（操作步驟）**：提供 1~5 步的操作流程與欄位用途。
2. **搜尋條件輸入**：填寫段數、最多連結數，以及每段機場/日期/必經機場/出關停留偏好。
3. **搜尋連結**：送出後顯示可直接點擊的 Skyscanner 連結清單。

> 更完整操作文件請見：`docs_usage.md`

## Python 程式使用方式

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
        ),
        SegmentPreference(
            origins=["LHR"],
            destinations=["TPE"],
            depart_from=date(2026, 3, 10),
            depart_to=date(2026, 3, 12),
        ),
    ],
    max_queries=50,
)

queries = generate_queries(config)
for q in queries[:3]:
    print(q.to_skyscanner_url())
```

## 測試

```bash
python -m unittest -q
```
