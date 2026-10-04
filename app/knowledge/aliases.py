ALIASES = {
    'HPU': {'hpu','hydraulic power unit','hydraulic unit','hp unit','hydraulic power pack','hydraulic pack','the unit'},
    'IV-21': {'iv-21','iv21','isolation valve','isolation valve 21'},
    'PS-04': {'ps-04','ps04','p04','pressure sensor 04','pressure sensor 04 (ps-04)','pressure sensor 04'},
    'PS-04A': {'ps-04a','ps04a','p04a','p.s.04-a','pressure sensor 04a','pressure sensor 04a (ps-04a)'},
    'PS-40': {'ps-40','ps40','p40','pressure sensor 40'},
    'PLC-03': {'plc-03','hcs controller','aegis controller','controller'},
    'A17': {'a17','alarm a17','hydraulic pressure low'},
    'A18': {'a18','alarm a18','hydraulic pressure high'},
    'A19': {'a19','alarm a19','pressure sensor signal invalid'},
}

def normalize_alias(value: str) -> str | None:
    v=' '.join(value.lower().replace('–','-').replace('—','-').split())
    for canonical, aliases in ALIASES.items():
        if v in aliases: return canonical
    return None
