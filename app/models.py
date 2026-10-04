from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any
import json

@dataclass
class Source:
    source_id: str
    path: str
    filename: str
    file_type: str
    trust: str
    trust_score: float
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    locator: str
    text: str
    modality: str = 'text'
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Fact:
    fact_id: str
    subject: str
    predicate: str
    value: Any
    source_id: str
    locator: str
    evidence_text: str
    trust: str
    confidence: float = 1.0
    valid_from_firmware: str | None = None
    valid_before_firmware: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

def dumps(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
