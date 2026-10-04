from pathlib import Path
from app.ingestion.loaders import ingest_tree
from app.knowledge.facts import extract_facts
from app.knowledge.store import KnowledgeStore

def build(data_dir,out_dir='artifacts'):
    sources,chunks=ingest_tree(data_dir)
    facts=extract_facts(sources,chunks)
    store=KnowledgeStore(out_dir); store.sources=sources; store.chunks=chunks; store.facts=facts; store.save()
    return store
