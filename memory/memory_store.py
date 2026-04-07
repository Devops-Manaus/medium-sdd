import json
import time
from pathlib import Path


class MemoryStore:
    """
    Memória simples em 3 camadas.
    Sem embeddings no início — JSON puro é suficiente para começar.

    working   → estado da sessão atual (RAM, some ao terminar)
    episodic  → log do que aconteceu (arquivo JSON persistente)
    procedural → receitas de correção que funcionaram (arquivo JSON persistente)
    """

    def __init__(self, path: str = ".memory"):
        self.base = Path(path)
        self.base.mkdir(exist_ok=True)

        self._working: dict = {}

        self._episodic   = self._load("episodic.json")
        self._procedural = self._load("procedural.json")


    def set(self, key: str, value):
        self._working[key] = value

    def get(self, key: str, default=None):
        return self._working.get(key, default)



    def log_event(self, event: str, details: dict):
        self._episodic.append({
            "ts": time.time(),
            "event": event,
            "details": details
        })
        self._save("episodic.json", self._episodic)

    def get_events(self, event_type: str = None, limit: int = 10) -> list:
        events = self._episodic
        if event_type:
            events = [e for e in events if e["event"] == event_type]
        return events[-limit:]


    def learn(self, problem_pattern: str, solution: str, context: str = ""):
        """
        Salva uma receita de correção que funcionou.
        Ex: problema 'placeholder em requisitos' → solução 'buscar requirements page'
        """
        self._procedural.append({
            "pattern":  problem_pattern,
            "solution": solution,
            "context":  context,
            "uses":     0,
            "ts":       time.time()
        })
        self._save("procedural.json", self._procedural)

    def recall(self, problem: str) -> str | None:
        """Busca solução conhecida por substring matching."""
        for proc in reversed(self._procedural):
            if proc["pattern"].lower() in problem.lower():
                proc["uses"] += 1
                self._save("procedural.json", self._procedural)
                return proc["solution"]
        return None

    def get_lessons_for_prompt(self, limit: int = 3) -> str:
        """
        Retorna lições aprendidas formatadas para injetar no prompt.
        Modelos locais se beneficiam de exemplos concretos no contexto.
        """
        recent = self._procedural[-limit:]
        if not recent:
            return ""

        lines = ["Lições de execuções anteriores (aplique estas correções):"]
        for p in recent:
            lines.append(f"- Problema: {p['pattern']}")
            lines.append(f"  Solução:  {p['solution']}")
        return "\n".join(lines)


    def _load(self, filename: str) -> list:
        p = self.base / filename
        return json.loads(p.read_text()) if p.exists() else []

    def _save(self, filename: str, data):
        (self.base / filename).write_text(
            json.dumps(data, indent=2, ensure_ascii=False)
        )