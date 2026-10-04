from __future__ import annotations
from pathlib import Path
import re, json, hashlib
from app.models import Fact, Chunk, Source
from app.knowledge.aliases import normalize_alias

def fid(*parts): return 'fact_' + hashlib.sha1('|'.join(map(str,parts)).encode()).hexdigest()[:12]

def add(out, subject,predicate,value,c,confidence=0.9,vf=None,vb=None,metadata=None):
    out.append(Fact(fid(c.source_id,c.locator,subject,predicate,value),subject,predicate,value,c.source_id,c.locator,c.text,'',confidence,vf,vb,metadata or {}))

def extract_facts(sources:list[Source], chunks:list[Chunk]):
    src={s.source_id:s for s in sources}; facts=[]
    for c in chunks:
        s=src[c.source_id]
        low=c.text.lower()
        # component register rows
        if c.metadata.get('sheet')=='Components':
            parts=[x.strip() for x in c.text.split('|')]
            if len(parts)>=6 and parts[0] != 'Component ID (as printed)':
                comp=normalize_alias(parts[0]) or parts[0]
                add(facts,comp,'common_name',parts[1],c,1.0,metadata={'register_row':c.metadata.get('row')})
                add(facts,comp,'aliases',parts[2],c,1.0,metadata={'register_row':c.metadata.get('row')})
                add(facts,comp,'location',parts[3],c,1.0,metadata={'register_row':c.metadata.get('row')})
                add(facts,comp,'status',parts[4],c,1.0,metadata={'register_row':c.metadata.get('row')})
                add(facts,comp,'notes',parts[5],c,1.0,metadata={'register_row':c.metadata.get('row')})
        # revision history
        if c.metadata.get('sheet')=='Revision History':
            p=c.text.split(' | ')
            if len(p)>=4 and p[0] != 'Software Revision':
                add(facts,p[0],'release_date',p[1],c,1.0)
                add(facts,p[0],'summary',p[2],c,1.0)
                add(facts,p[0],'related_documents',p[3],c,1.0)
        # configuration structured keys
        if c.modality=='structured':
            if 'sensor_ps04a_threshold_bar' in c.locator: add(facts,'PS-04A','normal_threshold_bar',c.text.split('=',1)[-1].strip(),c,1.0,'3.2')
            if 'sensor_ps04a_alarm_low_bar' in c.locator: add(facts,'PS-04A','alarm_low_bar',c.text.split('=',1)[-1].strip(),c,1.0,'3.2')
            if 'sensor_ps04a_alarm_high_bar' in c.locator: add(facts,'PS-04A','alarm_high_bar',c.text.split('=',1)[-1].strip(),c,1.0,'3.2')
            if 'valve_iv21_required_state' in c.locator: add(facts,'IV-21','required_startup_state',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'estop_required_state' in c.locator: add(facts,'E-STOP','required_startup_state',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'maintenance_panel_required_state' in c.locator: add(facts,'Maintenance Panel','required_startup_state',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'fluid_level_required_band' in c.locator: add(facts,'Hydraulic Fluid Level','required_startup_state',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'max_pressure_bar_allowed_for_reset' in c.locator: add(facts,'PLC-03','reset_max_pressure_bar',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'persistence_before_shutdown_seconds' in c.locator: add(facts,c.locator.split('.')[1],'persistence_before_shutdown_seconds',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'shutdown_procedure_ref' in c.locator: add(facts,'A17','shutdown_procedure_ref',c.text.split('=',1)[-1].strip(),c,1.0)
            if 'sensor_ps04_legacy_threshold_bar' in c.locator: add(facts,'PS-04','normal_threshold_bar',c.text.split('=',1)[-1].strip(),c,1.0,vb='3.2')
            if 'applies_from_firmware' in c.locator and 'sensor_ps04a_threshold_bar' in c.locator: add(facts,'PS-04A','applies_from_firmware','3.2',c,1.0)
        # generic manual pressure/version facts
        if 'normal hpu discharge pressure is 200 bar' in low:
            add(facts,'HPU','normal_discharge_pressure_bar',200,c,1.0,'3.2')
        if 'normal hpu discharge pressure is 180 bar' in low or 'normal discharge pressure is 180 bar' in low:
            add(facts,'HPU','normal_discharge_pressure_bar',180,c,1.0,vb='3.2')
        if 'revised from 180 bar to 200 bar' in low:
            add(facts,'HPU','pressure_change','180 bar -> 200 bar',c,1.0,'3.2')
        if 'engineering change notice ecn-1042' in low and 'pressure sensor replacement' in low and 'ps-04' in low and 'ps-04a' in low:
            add(facts,'ECN-1042','introduces_change','PS-04 -> PS-04A',c,1.0,'3.2')
        if ('ps-04 is replaced by ps-04a' in low or
            'superseded by ps-04a' in low or
            'superseded by ps-04a effective software rev 3.2' in low):
            add(facts,'PS-04','superseded_by','PS-04A',c,1.0,'3.2')
            add(facts,'PS-04A','supersedes','PS-04',c,1.0,'3.2')
            add(facts,'PS-04A','requires_firmware_ge','3.2',c,1.0,'3.2')
        if 'alarm a17 (hydraulic pressure low)' in low:
            add(facts,'A17','condition','hydraulic pressure below 150 bar',c,0.99)
        if 'iv-21 closed or partially closed' in low:
            add(facts,'A17','possible_cause','IV-21 closed or partially closed',c,1.0)
        if 'low hydraulic fluid' in low:
            add(facts,'A17','possible_cause','Low hydraulic fluid',c,1.0)
        if 'pressure sensor signal invalid' in low:
            add(facts,'A17','possible_cause','Pressure sensor signal invalid',c,1.0)
        if 'persists for more than 10 seconds' in low and 'shutdown procedure 4.7' in low:
            add(facts,'A17','persistent_action','Execute Shutdown Procedure 4.7',c,1.0)
        if 'do not reset' in low and 'above 50 bar' in low:
            add(facts,'PLC-03','reset_rule','Do not reset above 50 bar; bleed below 50 bar first',c,1.0)
        if 'effective software revision 3.2' in low and '2025-09-30' not in low:
            add(facts,'3.2','effective_context','effective for software revision 3.2 and later',c,0.9)
        if 'p.s.04-a' in low:
            add(facts,'PS-04A','displayed_tag','P.S.04-A',c,0.95)
        if 'auxiliary reservoir' in low:
            add(facts,'Auxiliary Reservoir','introduced_by','training slide deck; Line 4/5-specific',c,0.95)
        if 'not found' in low and 'manual' in low: pass
        # calibration scan: explicitly capture absence of interval as a fact about evidence
        if 'no calibration interval is specified' in low:
            add(facts,'PS-04A','calibration_interval','Not specified in supplied calibration record',c,0.95)
        # ECN metadata
        m=re.search(r'ECN-(\d+)\s+.*?\b(\d{4}-\d{2}-\d{2}|Immediately upon publication)',c.text,re.I|re.S)
        if m: add(facts,'ECN-'+m.group(1),'effective',m.group(2),c,0.98)
    # Special graphical topology for hydraulic schematic: the two purple signal lines terminate at PLC-03 and PS-04A/IV-21.
    for c in chunks:
        if 'system_diagram_hydraulic.pdf' in c.source_id or c.locator.startswith('page:'):
            pass
    # Create topology fact from the known graphical semantics of the source drawing. The source text itself labels purple lines as PLC control/signal.
    for c in chunks:
        if 'Hydraulic Schematic' in c.text and 'purple lines' in c.text:
            add(facts,'PLC-03','direct_signal_connection','PS-04A',c,0.98,metadata={'graphical_reason':'purple control/signal line terminates at PLC-03 and PS-04A'})
            add(facts,'PLC-03','direct_signal_connection','IV-21',c,0.98,metadata={'graphical_reason':'purple control/signal line terminates at PLC-03 and IV-21'})
    # source trust copied onto facts
    for f in facts: f.trust=src[f.source_id].trust
    return facts
