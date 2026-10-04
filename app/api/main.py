from fastapi import FastAPI
from pydantic import BaseModel
from app.knowledge.store import KnowledgeStore
from app.retrieval.search import HybridRetriever
from app.answer import AnswerEngine

app=FastAPI(title='Aegis Knowledge API',version='0.1.0')
class Question(BaseModel): question:str; use_llm:bool=True

def engine():
    s=KnowledgeStore('artifacts'); s.load(); return AnswerEngine(HybridRetriever(s.chunks,s.facts,s.sources))

@app.get('/')
def root(): return {'service':'Aegis Knowledge API','status':'ok'}
@app.post('/ask')
def ask(q:Question): return engine().answer(q.question,q.use_llm)
