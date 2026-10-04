from __future__ import annotations
import argparse, json, csv
from pathlib import Path
from app.ingestion.pipeline import build
from app.knowledge.store import KnowledgeStore
from app.retrieval.search import HybridRetriever
from app.answer import AnswerEngine

ROOT=Path(__file__).resolve().parents[1]

def load_or_build(data_dir,out_dir):
    p=Path(out_dir)
    if not (p/'facts.json').exists(): return build(data_dir,out_dir)
    s=KnowledgeStore(out_dir); s.load(); return s

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('ingest'); i.add_argument('--data-dir',required=True); i.add_argument('--out-dir',default='artifacts')
    a=sub.add_parser('ask'); a.add_argument('question'); a.add_argument('--data-dir',default='data/aegis-dataset/aegis-dataset'); a.add_argument('--out-dir',default='artifacts'); a.add_argument('--no-llm',action='store_true')
    e=sub.add_parser('evaluate'); e.add_argument('--data-dir',default='data/aegis-dataset/aegis-dataset'); e.add_argument('--out-dir',default='artifacts')
    args=ap.parse_args()
    if args.cmd=='ingest':
        s=build(args.data_dir,args.out_dir); print(f'Ingested {len(s.sources)} sources, {len(s.chunks)} chunks, {len(s.facts)} facts.')
    elif args.cmd=='ask':
        s=load_or_build(args.data_dir,args.out_dir); r=HybridRetriever(s.chunks,s.facts,s.sources); print(json.dumps(AnswerEngine(r).answer(args.question,not args.no_llm),indent=2,ensure_ascii=False))
    elif args.cmd=='evaluate':
        s=load_or_build(args.data_dir,args.out_dir); r=HybridRetriever(s.chunks,s.facts,s.sources); engine=AnswerEngine(r)
        qs=[
        'What must be true before starting the Hydraulic Power Unit?',
        'What is the current normal operating pressure for the HPU, and under what conditions does that apply?',
        'What does alarm A17 indicate, and what are its possible causes?',
        'Is PS-04 the same component as PS-04A?',
        'Which document introduced the change from PS-04 to PS-04A?',
        'Which components connect directly to the HCS controller, according to the hydraulic schematic?',
        'What action is required if alarm A17 persists for more than 10 seconds?',
        'Under what circumstances must the controller not be reset?',
        'What was the operating pressure threshold before software revision 3.2, and what changed it?',
        'Which alarm is associated with a pressure sensor reading below 150 bar?',
        'According to the component register, what is the location of the isolation valve IV-21?',
        'Does the training slide deck introduce any component or alarm not found in the manuals?',
        'What sensor ID appears on the diagnostics screenshot, and does it match a known component',
        'Per the revision history, when did software revision 3.2 take effect, and what changed alongside it?',
        'What does sensor_ps04a_threshold_bar in the configuration export correspond to in the operator manual\'s terminology?',
        'Does the 200 bar threshold apply to all Aegis HCS units, or only some?',
        'Is PS-04 the same as PS-40?',
        'What was the pressure limit before revision 3.2?',
        'What is the maximum continuous operating temperature of PS-04A?',
        'What is the calibration interval for the electrical system diagram\'s voltage sensor?',
        'Who approved engineering bulletin ECN-1058?',
        'What is the mean time between failures for the isolation valve IV-21?',
        'Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?']
        results=[]
        for i,q in enumerate(qs,1):
            ans=engine.answer(q,use_llm=False)
            results.append({'id':i,**ans})
        # Benchmark labels are intentionally compact and human-auditable.
        expected={
        1:['normal','iv-21','open','reset','closed'],2:['200 bar','3.2','180 bar'],3:['a17','150 bar','iv-21','fluid','sensor'],4:['no','ps-04a'],5:['ecn-1042'],6:['ps-04a','iv-21','plc-03'],7:['shutdown procedure 4.7','10 seconds'],8:['above 50 bar','below 50 bar'],9:['180 bar','ecn-1042','200 bar','ps-04a'],10:['a17','150 bar'],11:['hydraulic module'],12:['auxiliary reservoir','no new alarm'],13:['p.s.04-a','ps-04a'],14:['2025-09-30','ps-04a','200 bar'],15:['200 bar','normal'],16:['no','3.2'],17:['no','ps-40','coolant'],18:['180 bar'],19:['cannot be determined','not establish'],20:['cannot be determined','not establish'],21:['cannot be determined','not establish'],22:['cannot be determined','not establish'],23:['cannot be determined','not establish']}
        def score(i,text):
            t=' '.join(text.lower().replace('–','-').replace('—','-').split())
            hits=0
            for k in expected[i]:
                kk=' '.join(k.lower().split())
                # Treat semantically equivalent abstention wording as a match.
                if kk in t or (kk=='no new alarm' and ('does not introduce a new alarm' in t or 'does not introduce any new alarm' in t)):
                    hits += 1
            return hits/len(expected[i])
        for row in results:
            row['keyword_coverage']=round(score(row['id'],row['answer']),3)
            row['abstained']=row['id']>=19 and ('cannot be determined' in row['answer'].lower() or 'not establish' in row['answer'].lower())
        coverage=sum(r['keyword_coverage'] for r in results)/len(results)
        abst=sum(r['abstained'] for r in results[18:])/5
        summary={'questions':23,'mean_keyword_coverage':round(coverage,3),'correct_abstention_rate_q19_q23':round(abst,3),'note':'Keyword coverage is a transparent baseline metric, not final semantic accuracy. Evidence coverage and exactness must also be reviewed.'}
        Path(args.out_dir).mkdir(exist_ok=True,parents=True); Path(args.out_dir,'evaluation_results.json').write_text(json.dumps({'summary':summary,'results':results},indent=2,ensure_ascii=False), encoding='utf-8')
        with open(Path(args.out_dir,'evaluation_results.csv'),'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['id','question','answer','keyword_coverage','abstained']); w.writeheader(); w.writerows([{k:r.get(k) for k in w.fieldnames} for r in results])
        print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
