"""Independently authored materials-bench fixtures; no study or review source."""
import json

REFERENCE = 'A reference tile was rescanned before every batch.'
REPEATS = 'Every tile was scanned twice.'
TEXT = ('[Page 1]\nSynthetic ceramic-tile bench exercise.\n' + REFERENCE + '\n' + REPEATS +
        '\n[Page 2]\nThe chamber temperature was not logged.\n'
        'Tile colour | Signal units\nAmber | 4.6\nViolet | 7.3\n')
SOURCES = {'synthetic-bench.pdf': TEXT}
REPORT = '''# Overall synopsis
A **fictional** materials-bench exercise, for software testing only.

| Tile | Signal units |
| --- | --- |
| Amber | 4.6 |
| Violet | 7.3 |

# Major strengths
* Strength: The reference tile was checked before each batch.
* Evidence: "A reference tile was rescanned before every batch."

# Directly supported concerns
* Concern: The calibration log does not identify instrument serials.
* Evidence: The example does not specify instrument serials.
* Concern: Each tile appears to have been scanned once.
* Evidence: "Every tile was scanned twice."

# Verification prompts
* Check: Confirm chamber temperature control against the instrument log.
* Reason: Drift could affect the synthetic signal readings.

# Extraction limits
* Limit: This is a deliberately incomplete fictional document.

# Overall confidence
* Confidence: Requires human inspection.
'''

def assessor(*, prompt, schema, max_tokens):
    labels = schema['properties']['items']['items']['properties']['label']['enum']
    items = []
    for label in labels:
        quote = REFERENCE if label == 'S1' else REPEATS
        verdict = 'correct' if label == 'C2' else 'unresolved' if label in ('C1', 'P1') else 'supported'
        items.append(dict(label=label, verdict=verdict, quote=quote,
            reason='Scripted fixture response; a located sentence does not settle its interpretation.',
            correction='The example explicitly reports two scans.' if label == 'C2' else '',
            surviving_point='', duplicate_of='', reviewer_check='Inspect the original bench log.',
            evidence=[dict(quote=quote, role='contradicts' if label == 'C2' else 'supports')]))
    return {'items': items}

def verified():
    import source_verification as sv
    return sv.verify_report(REPORT, SOURCES, assessor, budget=100000, unexamined=[]).as_dict()

def cards():
    import evidence_cards as ec
    return ec.build_cards(verified(), SOURCES)

def job(**overrides):
    import human_evidence_appendix as hea
    value = dict(status='complete', progress=[], filename='synthetic-bench.pdf', report=REPORT,
        appendix=hea.render_human_evidence_appendix(hea.build_evidence_cards(REPORT)), text=TEXT,
        sources=SOURCES, verification_sources=SOURCES, source_verification={'verification':verified()},
        development_mode=False, error=None)
    value.update(overrides)
    return value

def pdf_bytes(lines):
    """Original minimal uncompressed PDF generator; one line per page."""
    font = 3 + 2 * len(lines)
    objects = ['<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids ['+' '.join(str(3+2*i)+' 0 R' for i in range(len(lines)))+'] /Count '+str(len(lines))+' >>']
    for i, line in enumerate(lines):
        escaped=line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
        stream='BT /F1 11 Tf 50 740 Td ('+escaped+') Tj ET'
        objects += [f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4+2*i} 0 R /Resources << /Font << /F1 {font} 0 R >> >> >>',
                    f'<< /Length {len(stream)} >>\nstream\n{stream}\nendstream']
    objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    data=b'%PDF-1.4\n';offsets=[]
    for i,obj in enumerate(objects,1):
        offsets.append(len(data));data+=(f'{i} 0 obj\n'+obj+'\nendobj\n').encode('ascii')
    start=len(data);data+=(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'+''.join(f'{n:010d} 00000 n \n' for n in offsets)+
        f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n').encode('ascii')
    return data

class Reply:
    """In-memory urllib response; protocol-only fixture."""
    status=200
    def __init__(self, content='Fixture response.', **message):
        self.data=json.dumps({'choices':[{'message':{'content':content,**message},'finish_reason':'stop'}],
                              'usage':{'completion_tokens':9}}).encode()
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self):return self.data
