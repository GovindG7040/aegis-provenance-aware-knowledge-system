from __future__ import annotations
from pathlib import Path
import json
from app.models import Source,Chunk,Fact

class KnowledgeStore:
    def __init__(self, out_dir='artifacts'):
        self.out=Path(out_dir); self.out.mkdir(parents=True,exist_ok=True)
        self.sources=[]; self.chunks=[]; self.facts=[]
    def save(self):
        (self.out/'sources.json').write_text(json.dumps([s.__dict__ for s in self.sources],indent=2,ensure_ascii=False), encoding='utf-8')
        (self.out/'chunks.jsonl').write_text('\n'.join(json.dumps(c.__dict__,ensure_ascii=False) for c in self.chunks), encoding='utf-8')
        (self.out/'facts.json').write_text(json.dumps([f.to_dict() for f in self.facts],indent=2,ensure_ascii=False,default=str), encoding='utf-8')
    def load(self):
        self.sources=[Source(**x) for x in json.loads((self.out/'sources.json').read_text(encoding='utf-8'))]
        self.chunks=[]
        for line in (self.out/'chunks.jsonl').read_text(encoding='utf-8').splitlines():
            if line.strip(): self.chunks.append(Chunk(**json.loads(line)))
        self.facts=[Fact(**x) for x in json.loads((self.out/'facts.json').read_text(encoding='utf-8'))]
