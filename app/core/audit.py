import hashlib, json, time
from pathlib import Path

class AuditLog:
    def __init__(self, path="runs/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.prev = self._last_hash()

    def _last_hash(self):
        if not self.path.exists() or self.path.stat().st_size == 0:
            return "GENESIS"
        return json.loads(self.path.read_text().strip().splitlines()[-1])["hash"]

    def write(self, event: dict) -> str:
        record = {"ts": time.time(), "prev_hash": self.prev, **event}
        body = json.dumps(record, sort_keys=True, ensure_ascii=False)
        record["hash"] = hashlib.sha256(body.encode()).hexdigest()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.prev = record["hash"]
        return record["hash"]

    def verify(self) -> bool:
        prev = "GENESIS"
        for line in self.path.read_text().splitlines():
            rec = json.loads(line)
            h = rec.pop("hash")
            if rec["prev_hash"] != prev:
                return False
            body = json.dumps(rec, sort_keys=True, ensure_ascii=False)
            if hashlib.sha256(body.encode()).hexdigest() != h:
                return False
            prev = h
        return True
