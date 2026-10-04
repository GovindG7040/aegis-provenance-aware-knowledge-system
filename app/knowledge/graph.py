"""Small graph projection used for documentation and optional downstream analysis."""
from collections import defaultdict

def build_edges(facts):
    edges=defaultdict(list)
    for f in facts:
        if f.predicate in {'supersedes','superseded_by','direct_signal_connection','possible_cause'}:
            edges[f.subject].append((f.predicate,f.value,f.source_id,f.locator))
    return dict(edges)
