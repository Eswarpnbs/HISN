import json, ollama

class OllamaLLM:
    """Local LLM via Ollama, JSON mode, temperature 0 for repeatability."""
    def __init__(self, model="qwen2.5:7b"):
        self.model, self.client = model, ollama.Client()

    def __call__(self, system, user):
        r = self.client.chat(model=self.model, format="json",
                             messages=[{"role": "system", "content": system},
                                       {"role": "user", "content": user}],
                             options={"temperature": 0, "num_ctx": 8192})
        return json.loads(r["message"]["content"])
