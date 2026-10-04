from pathlib import Path
from app.ingestion.loaders import ingest_tree

def test_all_source_formats():
    root=Path('data/aegis-dataset/aegis-dataset')
    if not root.exists(): return
    sources,chunks=ingest_tree(str(root))
    assert len(sources)==20
    assert len(chunks)>0
