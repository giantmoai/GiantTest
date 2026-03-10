# GiantTest

這個小工具可協助你在 Skyscanner 規劃「便宜機票」搜尋條件，支援：

- 自選機場（每段可多選出發/抵達機場）
- 時間範圍（每段可設出發日期區間）
- 多段行程（最多四段）
- 每段必經機場（`via_airports`）
- 中間機場是否可出關停留（`allow_exit_transit`）

## 使用方式

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
