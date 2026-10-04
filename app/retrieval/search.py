from __future__ import annotations
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HybridRetriever:
    def __init__(self,chunks,facts,sources):
        self.chunks=chunks; self.facts=facts; self.sources={s.source_id:s for s in sources}
        texts=[c.text for c in chunks] or ['']
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),lowercase=True,sublinear_tf=True)
        self.matrix=self.vectorizer.fit_transform(texts)
    def search(self,query,k=8):
        q=self.vectorizer.transform([query]); sims=cosine_similarity(q,self.matrix).ravel()
        idx=sims.argsort()[::-1][:k]
        out=[]
        for i in idx:
            if sims[i]<=0: continue
            c=self.chunks[i]; out.append({'type':'chunk','score':float(sims[i]),'chunk':c.__dict__,'source':self.sources[c.source_id].__dict__})
        # Structured fact boost: exact canonical identifiers and important numeric terms.
        ql=query.lower()
        for f in self.facts:
            score=0.0
            terms=[f.subject.lower(),f.predicate.lower(),str(f.value).lower()]
            for t in terms:
                if t and t in ql: score += 0.22
            if score:
                out.append({'type':'fact','score':score,'fact':f.to_dict(),'source':self.sources[f.source_id].__dict__})
        return sorted(out,key=lambda x:x['score'],reverse=True)[:k+6]
