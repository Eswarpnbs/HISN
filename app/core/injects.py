import yaml
from pathlib import Path
from .events import Event

INJ_DIR = Path("scenarios/injects")

def available():
    return sorted(p.stem for p in INJ_DIR.glob("*.yaml"))

def load_injects(names):
    evs = []
    for n in names or []:
        data = yaml.safe_load(open(INJ_DIR / f"{n}.yaml", encoding="utf-8"))
        for e in data["events"]:
            evs.append(Event(id=e["id"], t=int(e["t"]), kind=e["kind"], audience=tuple(e["audience"]),
                             payload=e.get("payload", {}), act=int(e.get("act", 0))))
    return evs
