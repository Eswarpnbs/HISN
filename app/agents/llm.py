import json
from collections import Counter

class OllamaLLM:
    """Local LLM via Ollama, JSON mode, temperature 0 for repeatability."""
    def __init__(self, model="qwen2.5:7b", temperature=0, seed=None):
        import ollama   # imported here so the voting logic can be tested without Ollama installed
        self.model, self.client, self.temperature, self.seed = model, ollama.Client(), temperature, seed

    def __call__(self, system, user):
        opts = {"temperature": self.temperature, "num_ctx": 8192}
        if self.seed is not None: opts["seed"] = self.seed
        r = self.client.chat(model=self.model, format="json",
                             messages=[{"role": "system", "content": system},
                                       {"role": "user", "content": user}],
                             options=opts)
        return json.loads(r["message"]["content"])


class VotingLLM:
    """Majority vote over k answers (added 8 Nov 2026). Answer 1 is the usual temperature-0 answer; answers 2..k are
    sampled (temperature 0.7, fixed seeds, so a re-run gives the same votes). The proposed_action chosen by most answers
    wins and that answer's citations are kept; with no strict majority the temperature-0 answer stands. All votes are
    returned under "_votes" and written to the audit log. The fixed gates then check the winner exactly as before."""
    def __init__(self, samplers):
        self.samplers = samplers

    @classmethod
    def ollama(cls, model, k=3):
        return cls([OllamaLLM(model)] + [OllamaLLM(model, temperature=0.7, seed=i) for i in range(1, k)])

    def __call__(self, system, user):
        outs = []
        for s in self.samplers:
            try:
                outs.append(s(system, user))
            except Exception as ex:   # one failed sample does not sink the decision
                outs.append({"proposed_action": None, "_error": str(ex)})
        votes = [o.get("proposed_action") for o in outs]
        counts = Counter(v for v in votes if v)
        if not counts:
            raise RuntimeError("all samples failed")
        top, n = counts.most_common(1)[0]
        winner = next(o for o in outs if o.get("proposed_action") == top) if n * 2 > len(outs) else outs[0]
        if winner.get("proposed_action") is None:
            winner = next(o for o in outs if o.get("proposed_action"))
        return {**winner, "_votes": votes}
