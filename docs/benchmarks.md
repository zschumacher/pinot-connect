Benchmarks were performed using a pinot quickstart batch cluster and the `githubComplexTypeEvents` table. All times for
benchmarks are recorded in milliseconds.  These benchmarks compare `pinot_connect` performance to `pinotdb` performance.

---
## Running benchmarks
To run the benchmarks yourself, start the quickstart cluster referenced on the [**homepage**](index.md).  Then run:
```bash
git clone git@github.com:zschumacher/pydapper.git
cd pydapper
asdf install
poetry install
poetry run python scripts/pinotdb_benchmarks.py 
```

!!! note
    `pinotdb` returns rows untouched as a list of lists, so the benchmark for `pinot_connect` uses a `list_row` factory to
    mirror that behavior in all benchmarks.  Additionally, python garbage collection is disabled for all benchmarks.

---
## Large query
```sql
select * from githubComplexTypeEvents limit 1000
```

!!! note
    Large queries see a much larger performance improvement mostly due to faster json deserialization via `orjson`.  The 
    larger the query result becomes, the better *pinot_connect* will perform when compared to *pinotdb*.

### Sync
Run the query 100 times sequentially
!!! note ""
    === "fetchone"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3211.60 |      32.12 |      31.80 |      34.24 |
        | **pinotdb** |    3820.82 |      38.21 |      38.08 |      39.46 |
        | **diff%**   |     18.97% |     18.97% |     19.75% |     15.24% |
    === "fetchmany"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3278.68 |      32.79 |      32.54 |      34.92 |
        | **pinotdb** |    3898.60 |      38.99 |      38.99 |      40.55 |
        | **diff%**   |     18.91% |     18.91% |     19.82% |     16.12% |
    === "fetchall"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3278.01 |      32.78 |      32.66 |      34.18 |
        | **pinotdb** |    3908.55 |      39.09 |      39.16 |      40.42 |
        | **diff%**   |     19.24% |     19.24% |     19.91% |     18.26% |

### Async
Run the query 100 times concurrently
!!! note ""
    === "fetchone"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    1737.41 |
        | **pinotdb** |    2278.16 |
        | **diff%**   |     31.12% |
    === "fetchmany"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    1805.03 |
        | **pinotdb** |    2359.02 |
        | **diff%**   |     30.69% |
    === "fetchall"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    1843.05 |
        | **pinotdb** |    2372.22 |
        | **diff%**   |     28.71% |


---
## Small query
```sql
select * from githubComplexTypeEvents limit 10
```

!!! note
    Smaller query results see less of a performance difference - the effects from `orjson` are diminished and the
    small improvements are due to the slightly more efficient cursor in `pinot_connect`

### Sync
Run the query 1000 times sequentially
!!! note ""
    === "fetchone"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3669.85 |       3.67 |       3.62 |       4.51 |
        | **pinotdb** |    3879.03 |       3.88 |       3.83 |       4.67 |
        | **diff%**   |      5.70% |      5.70% |      5.83% |      3.70% |
    === "fetchmany"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3721.37 |       3.72 |       3.70 |       4.43 |
        | **pinotdb** |    3896.81 |       3.90 |       3.81 |       4.80 |
        | **diff%**   |      4.71% |      4.71% |      3.04% |      8.41% |
    === "fetchall"
        |             |      total |        avg |     median |        p95 |
        | ----------- | ---------- | ---------- | ---------- | ---------- |
        | **pinot_connect** |    3660.49 |       3.66 |       3.59 |       4.55 |
        | **pinotdb** |    3886.63 |       3.89 |       3.80 |       4.59 |
        | **diff%**   |      6.18% |      6.18% |      5.72% |      0.92% |

### Async
Run the query 1000 times concurrently
!!! note ""
    === "fetchone"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    3364.68 |
        | **pinotdb** |    3405.71 |
        | **diff%**   |    1.22% |
    === "fetchmany"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    3256.76 |
        | **pinotdb** |    3306.85 |
        | **diff%**   |    1.54% |
    === "fetchall"
        |             |      total | 
        | ----------- | ---------- |
        | **pinot_connect** |    3325.85 |
        | **pinotdb** |    3379.53 |
        | **diff%**   |     1.61% |
