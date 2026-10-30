"""95% Wilson score intervals for small-sample accuracies (e.g. 13/14)."""
import math, re

def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)

def with_ci(frac):
    """'13/14' -> '13/14 (69-99%)'; anything that is not k/n is returned unchanged."""
    m = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", str(frac))
    if not m:
        return frac
    k, n = map(int, m.groups())
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({lo * 100:.0f}-{hi * 100:.0f}%)"
