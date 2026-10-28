"""Derive an empirical radio-link-failure profile from the Turkcell ITU AI/ML in 5G Challenge 2021 data.
Raw data stays outside the repo (~/rlf-data); only aggregate statistics are written to kb/rulepacks/network_profile.yaml.
Citation: Aktas, Alemdar, Ergut (2022), Computers & Electrical Engineering 99:107742."""
import csv, hashlib, statistics, sys, yaml
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)
RAW = Path.home() / "rlf-data"; X = RAW / "extracted"
num = lambda s: float(s.replace(",", "")) if s not in ("", None) else None
find = lambda name: next(X.rglob(name))

# 1) nearest weather station per radio site
nearest = {}
with open(find("distances.tsv"), encoding="utf-8") as f:
    r = csv.reader(f, delimiter="\t"); head = next(r)
    ws_cols = [i for i, h in enumerate(head) if h.startswith("WS_")]
    for row in r:
        if row[0].startswith("RL_"):
            i = min(ws_cols, key=lambda c: num(row[c]) if row[c] else 1e9)
            nearest[row[0]] = head[i]
print("sites with nearest station:", len(nearest))

# 2) daily weather per station: max temperature, total precipitation
tmax, rain = {}, defaultdict(float)
with open(find("met-real.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        k = (row["station_no"], row["datetime"][:10])
        t = num(row["temp_max"]) or num(row["temp"])
        if t is not None: tmax[k] = max(tmax.get(k, -99), t)
        p = num(row["precipitation"])
        if p is not None and p > 0: rain[k] += p
print("station-days with temperature:", len(tmax))

# 3) per site-day failure flag and unavailable seconds
fail, unavail = {}, defaultdict(float)
with open(find("rl-kpis.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        k = (row["site_id"], row["datetime"][:10])
        fail[k] = fail.get(k, False) or row["rlf"] == "True"
        u = num(row["unavail_second"])
        if u: unavail[k] += u
print("site-days:", len(fail), "| failure site-days:", sum(fail.values()))

# 4) join and compute conditional rates
joined = []
for (site, day), f_ in fail.items():
    st = nearest.get(site)
    if st and (st, day) in tmax:
        joined.append((f_, tmax[(st, day)], rain.get((st, day), 0.0), unavail.get((site, day), 0.0)))
temps = sorted(t for _, t, _, _ in joined)
hot_thr = temps[int(0.9 * len(temps))]
def rate(rows): return (sum(1 for x in rows if x[0]) / len(rows)) if rows else 0.0
hot = [x for x in joined if x[1] >= hot_thr]; other = [x for x in joined if x[1] < hot_thr]
rainy = [x for x in joined if x[2] >= 5.0]; dry = [x for x in joined if x[2] == 0.0]
out_min = [x[3] / 60 for x in joined if x[0] and x[3] > 0]
src = RAW / "RLF_Prediction_ITU_AIML_Challenge_Data" / "RLF_Prediction_ITU_AIML_Challenge_Data.7z"
prof = {
    "source": "Turkcell ITU AI/ML in 5G Challenge 2021, RLF prediction data (RegionA)",
    "source_url": "https://github.com/Turkcell/ITU-AIMLin5GChallenge-2021",
    "citation": "Aktas S., Alemdar H., Ergut S. (2022) Computers & Electrical Engineering 99:107742",
    "source_archive_sha256": hashlib.sha256(src.read_bytes()).hexdigest() if src.exists() else None,
    "licence_note": "No explicit licence in source repository; raw data not redistributed - aggregate statistics only.",
    "proxy_note": "Turkish operator microwave backhaul data used as a statistical proxy; not UAE data.",
    "n_link_days": len(joined), "n_failure_link_days": sum(1 for x in joined if x[0]),
    "p_rlf_base": round(rate(joined), 6),
    "hot_threshold_temp_c": hot_thr, "p_rlf_hot": round(rate(hot), 6), "p_rlf_not_hot": round(rate(other), 6),
    "rain_threshold_mm": 5.0, "p_rlf_rainy": round(rate(rainy), 6), "p_rlf_dry": round(rate(dry), 6),
    "relative_risk_hot": round(rate(hot) / rate(other), 2) if rate(other) else None,
    "relative_risk_rain": round(rate(rainy) / rate(dry), 2) if rate(dry) else None,
    "median_outage_minutes_on_failure_days": round(statistics.median(out_min), 1) if out_min else None,
}
Path("kb/rulepacks/network_profile.yaml").write_text(yaml.safe_dump(prof, sort_keys=False), encoding="utf-8")
for k in ("n_link_days", "n_failure_link_days", "p_rlf_base", "hot_threshold_temp_c", "p_rlf_hot", "p_rlf_not_hot",
          "relative_risk_hot", "p_rlf_rainy", "p_rlf_dry", "relative_risk_rain", "median_outage_minutes_on_failure_days"):
    print(f"{k:<40} {prof[k]}")
print("written kb/rulepacks/network_profile.yaml")
