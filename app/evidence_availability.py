"""Host-only review availability sidecar. Never changes prompts, results or retries.

Scope is context-local; absence of an event is UNKNOWN. Errors degrade only the
sidecar and are disclosed separately, never converted to manuscript criticisms.
"""
from __future__ import annotations
import contextlib
import base64
import contextvars
import functools
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sys
import uuid

_ACTIVE = contextvars.ContextVar('review_availability', default=None)
_SOURCE = contextvars.ContextVar('review_availability_source', default=None)
_STAGE = contextvars.ContextVar('review_availability_stage', default='UNSCOPED')
_REQUEST_REASON = contextvars.ContextVar('review_request_reason', default=None)

def request_reason(): return _REQUEST_REASON.get()

@contextlib.contextmanager
def request_context(reason):
    token = _REQUEST_REASON.set(reason)
    try: yield
    finally: _REQUEST_REASON.reset(token)

CAPTION = re.compile(r'^\s*(Table|Figure)\s+([A-Za-z]?\d+[A-Za-z]?)\s*[.:]\s*[^\n]+', re.I | re.M)
PAGE = re.compile(r'\[Page\s+(\d+)\]')

def sha(data): return hashlib.sha256(data).hexdigest()
def encoded(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
def storage_root():
    return Path(os.environ.get('QWEN_EVIDENCE_LEDGER_DIR') or Path(__file__).resolve().parents[1] / 'local_results' / 'review-evidence-availability')
def safe_id(value):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', str(value)): raise ValueError('Invalid sidecar job identifier')
    return str(value)

def _observe(method, *args, **kwargs):
    rec = _ACTIVE.get()
    if rec is None: return None
    try: return getattr(rec, method)(*args, **kwargs)
    except Exception as exc:
        rec.errors.append(f'{method}: {type(exc).__name__}: {exc}')
        logging.getLogger(__name__).warning('Evidence availability incomplete: %s', rec.errors[-1])
        return None

class Recorder:
    def __init__(self, job_id, root=None):
        self.directory = (Path(root) if root else storage_root()) / safe_id(job_id)
        self.started = False
        self.errors = []
        self.data = {'version': 1, 'job_id': job_id, 'authority': 'AVAILABILITY ONLY; NOT ACADEMIC VERIFICATION',
                     'sources': {}, 'objects': {}, 'unresolved': [], 'attempts': [], 'stages': [], 'requests': [], 'media': []}
        self.representations = []
    def _start(self):
        if not self.started:
            self.directory.mkdir(parents=True, mode=0o700, exist_ok=False)
            self.started = True
    def execution(self, phase, value):
        self.data.setdefault('execution', {})[phase] = value
        if phase == 'actual':
            self.data['execution'][phase].update(self.execution_totals())
        if self.started: self.persist()
    def execution_totals(self):
        requests = self.data['requests']
        return {'model_requests': len(requests),
                'model_responses': sum(r['state'] == 'RESPONSE_RECEIVED' for r in requests),
                'final_synthesis_requests': sum(r['stage'] == 'final-synthesis' for r in requests)}
    def artifact(self, data, suffix):
        self._start()
        name = sha(data) + suffix
        target = self.directory / name
        if not target.exists():
            with target.open('xb') as f:
                os.chmod(target, 0o600); f.write(data); f.flush(); os.fsync(f.fileno())
        elif target.read_bytes() != data: raise ValueError('Artifact identity mismatch')
        return {'file': name, 'sha256': sha(data), 'bytes': len(data)}
    def persist(self):
        if not self.started: return
        self.data['instrumentation_errors'] = list(self.errors)
        self.data['integrity_state'] = 'AUDIT_INCOMPLETE' if self.errors else 'RECORDED'
        for name, payload in [('LEDGER.json', encoded(self.data)), ('COVERAGE.md', coverage_notice(self.data).encode())]:
            tmp = self.directory / (name + '.tmp')
            with tmp.open('wb') as f:
                os.chmod(tmp, 0o600); f.write(payload); f.flush(); os.fsync(f.fileno())
            os.replace(tmp, self.directory / name)
    def begin_source(self, path):
        path = Path(path); raw = path.read_bytes(); sid = sha(raw)
        original = self.artifact(raw, path.suffix.lower() if re.fullmatch(r'\.[a-z0-9]+', path.suffix.lower()) else '.source')
        self.data['sources'].setdefault(sid, {'sha256': sid, 'original_name': path.name, 'artifact': original,
            'object_discovery': 'POSITIVE_CAPTIONS_ONLY; NOT AN EXHAUSTIVE INVENTORY'})
        source = self.data['sources'][sid]
        source['load_occurrences'] = source.get('load_occurrences', 0) + 1
        source.setdefault('observed_names', [])
        if path.name not in source['observed_names']: source['observed_names'].append(path.name)
        self.persist(); return sid
    def event(self, method, status, page=None, reason=None):
        if _SOURCE.get() is None: return
        self.data['attempts'].append({'source_sha256': _SOURCE.get(), 'method': method, 'status': status,
            'physical_page': page, 'reason': reason, 'scope': 'specified method/page only; no inference about other objects'})
        self.persist()
    def stage_event(self, name, state):
        if not self.started: return
        self.data['stages'].append({'stage': name, 'state': state, 'supply': 'ONLY REQUEST RECEIPTS ESTABLISH DELIVERY'})
        self.persist()
    def add_representation(self, obj, kind, text, provenance):
        artifact = self.artifact(text.encode(), '.txt')
        rid = 'rep-' + sha(encoded([obj['id'], kind, provenance, artifact['sha256']]))[:24]
        if any(r['id'] == rid for r in self.representations): return
        r = {'id': rid, 'object_id': obj['id'], 'kind': kind, 'artifact': artifact, 'provenance': provenance,
             'completeness': 'NOT_ESTABLISHED'}
        obj['representations'].append(r)
        self.representations.append(r)
    def document(self, sid, text, tables, notes):
        snapshot = self.artifact(text.encode(), '.txt')
        self.data['sources'][sid]['loaded_text'] = snapshot
        self.data['sources'][sid]['extraction_notes'] = list(notes)
        self.data['sources'][sid]['dedicated_table_blocks'] = len(tables)
        matches = list(CAPTION.finditer(text))
        for m in matches:
            pages = list(PAGE.finditer(text, 0, m.start()))
            page = int(pages[-1].group(1)) if pages else None
            kind, label = m.group(1).lower(), m.group(1).title() + ' ' + m.group(2)
            if page is None:
                artifact = self.artifact(m.group().encode(), '.txt')
                rep = {'id': 'unresolved-' + sha(encoded([sid, snapshot, m.start(), m.end()]))[:24],
                       'object_id': None, 'kind': 'unresolved_caption', 'artifact': artifact}
                self.representations.append(rep)
                self.data['unresolved'].append({'source_sha256': sid, 'label_claim': label,
                    'reason': 'Physical page unknown; no object identity invented', 'snapshot': snapshot,
                    'start': m.start(), 'end': m.end(), 'representation': rep}); continue
            oid = 'object-' + sha(encoded([sid, kind, label, page]))[:24]
            obj = self.data['objects'].setdefault(oid, {'id': oid, 'source_sha256': sid, 'type': kind,
                'label': label, 'physical_page': page, 'identification': 'EXPLICIT_CAPTION_IN_LOADED_TEXT',
                'representations': [], 'interpretation': 'UNKNOWN; SUPPLIED DOES NOT MEAN EXAMINED OR VERIFIED',
                'limitations': ['Extraction completeness and semantic interpretation are not established.']})
            self.add_representation(obj, 'caption', m.group(), {'snapshot': snapshot, 'start': m.start(), 'end': m.end()})
            # Page text may contain several objects. Preserve context without asserting a cell layout.
            next_page = PAGE.search(text, m.end())
            end = next_page.start() if next_page else len(text)
            self.add_representation(obj, 'source_context', text[m.start():end], {'snapshot': snapshot, 'start': m.start(), 'end': end})
            if kind == 'figure': obj['limitations'] = ['Caption/context recorded; plot acquisition and interpretation remain UNKNOWN unless separate receipts establish them.']
        for index, (page, block) in enumerate(tables):
            # Bind only an explicit caption in the acquisition, not an inferred Label header or page alone.
            caps = list(CAPTION.finditer(block))
            labels = {m.group(1).title() + ' ' + m.group(2) for m in caps if m.group(1).lower() == 'table'}
            candidates = [o for o in self.data['objects'].values() if o['source_sha256'] == sid and
                          o['physical_page'] == page and o['label'] in labels]
            source = re.search(r'^Source:\s*(.*)$', block, re.M)
            provenance = {'load_occurrence': self.data['sources'][sid]['load_occurrences'], 'acquisition_index': index, 'method': source.group(1) if source else 'UNKNOWN', 'physical_page': page}
            if len(candidates) == 1 and len(labels) == 1:
                self.add_representation(candidates[0], 'table_acquisition', block, provenance)
            else:
                artifact = self.artifact(block.encode(), '.txt')
                rep = {'id': 'unresolved-' + sha(encoded([sid, provenance, artifact['sha256']]))[:24],
                       'object_id': None, 'kind': 'unresolved_table_acquisition', 'artifact': artifact}
                self.representations.append(rep)
                self.data['unresolved'].append({'source_sha256': sid, 'provenance': provenance,
                    'artifact': artifact, 'representation': rep, 'reason': 'Ambiguous object binding; page/Label alone insufficient'})
        self.persist()
    def media(self, png, page, purpose):
        self.data['media'].append({'source_sha256': _SOURCE.get(), 'physical_page': page, 'purpose': purpose,
            'artifact': self.artifact(png, '.png'),
            'data_url_sha256': sha(('data:image/png;base64,' + base64.b64encode(png).decode('ascii')).encode()),
            'object_binding': 'UNKNOWN; page image does not prove any particular object was examined'})
        self.persist()
    def request_started(self, endpoint, raw):
        if not self.started or not endpoint.rstrip('/').endswith('/chat/completions'): return None
        rq = json.loads(raw)
        if 'messages' not in rq: return None
        strings = []
        for m in rq['messages']:
            c = m.get('content')
            if isinstance(c, str): strings.append(c)
            elif isinstance(c, list): strings.extend(p['text'] for p in c if isinstance(p, dict) and isinstance(p.get('text'), str))
        image_urls = [p.get('image_url', {}).get('url', '') for m in rq['messages'] if isinstance(m.get('content'), list) for p in m['content'] if isinstance(p, dict) and isinstance(p.get('image_url'), dict)]
        media = [dict(image_sha256=m['artifact']['sha256'], source_sha256=m['source_sha256'], physical_page=m['physical_page'], delivery='UNKNOWN') for m in self.data['media'] if any(sha(url.encode()) == m['data_url_sha256'] for url in image_urls)]
        members = []
        for rep in self.representations:
            text = (self.directory / rep['artifact']['file']).read_text()
            members.append({'representation_id': rep['id'], 'object_id': rep['object_id'],
                'presence': 'IN_EXACT_REQUEST' if text and any(text in s for s in strings) else 'NOT_PRESENT_EXACT_REPRESENTATION',
                'delivery': 'UNKNOWN'})
        override = request_reason()
        if override == 'resolved review configuration': override = None
        if image_urls:
            override = 'visual transcription: Instruct'
        elif 'chat_template_kwargs' not in rq:
            override = ((override + '; ') if override else '') + 'thinking controls omitted; effective model mode unknown'
        elif rq.get('response_format') and (rq.get('chat_template_kwargs') or {}).get('enable_thinking') is False:
            override = 'structured JSON output contract: Instruct'
        ticket = len(self.data['requests'])
        self.data['requests'].append({'sequence': ticket, 'stage': _STAGE.get(), 'endpoint': endpoint,
            'execution': {'enable_thinking': (rq.get('chat_template_kwargs') or {}).get('enable_thinking'),
                          'reasoning_effort': (rq.get('chat_template_kwargs') or {}).get('reasoning_effort'),
                          'max_tokens': rq.get('max_tokens'), 'image_count': len(image_urls),
                          'override': override},
            'request': self.artifact(raw, '.request.json'), 'source_sha256': _SOURCE.get(), 'state': 'PREPARED_DISPATCH_UNKNOWN', 'members': members, 'media': media})
        self.persist(); return ticket
    def request_finished(self, ticket, raw=None, error=None):
        if ticket is None: return
        r = self.data['requests'][ticket]
        r['state'] = 'RESPONSE_RECEIVED' if error is None else 'DISPATCH_FAILED_OR_UNCERTAIN'
        completion_receipt = False
        if raw is not None:
            r['response'] = self.artifact(raw, '.response.json')
            try:
                response = json.loads(raw)
                completion_receipt = isinstance(response, dict) and any(isinstance(c.get('message'), dict) for c in response.get('choices', []) if isinstance(c, dict))
                r['usage'] = response.get('usage')
                r['finish_reasons'] = [c.get('finish_reason') for c in response.get('choices', [])]
            except (ValueError, TypeError, AttributeError): r['response_parse'] = 'NOT_JSON'
        r['native_completion_receipt'] = completion_receipt
        if error is not None: r['error'] = error
        for image in r['media']: image['delivery'] = 'SUPPLIED' if error is None and completion_receipt else 'UNKNOWN'
        for member in r['members']:
            member['delivery'] = ('SUPPLIED' if member['presence'] == 'IN_EXACT_REQUEST' else 'NOT_PRESENT_EXACT_REPRESENTATION') if error is None and completion_receipt else 'UNKNOWN'
        self.persist()

def coverage_notice(data):
    lines = ['# Host-owned evidence coverage', '', 'Availability only. Not methodological criticism or academic verification.',
             'Supplied does not mean examined, understood or verified. Missing receipts mean UNKNOWN.', '']
    if data.get('instrumentation_errors'): lines.append('AUDIT INCOMPLETE: ' + '; '.join(data['instrumentation_errors']))
    for sid, source in sorted(data['sources'].items()):
        if source.get('dedicated_table_blocks') == 0:
            lines.append(f'- Source {sid[:12]}: no dedicated table blocks recorded; plain-text table evidence may still exist. Not proof of extraction failure or manuscript absence.')
    for obj in sorted(data['objects'].values(), key=lambda o: o['id']):
        lines.append(f"- {obj['label']} — source {obj['source_sha256'][:12]}, PDF p.{obj['physical_page']}: {len(obj['representations'])} recorded representations; completeness UNKNOWN.")
        lines.extend('  '+s for s in obj['limitations'])
        for r in data['requests']:
            states = sorted({m['delivery'] for m in r['members'] if m['object_id'] == obj['id']})
            if states: lines.append(f"  {r['stage']} request {r['sequence']}: {', '.join(states)} (exact representations only).")
    lines.append(f"Unresolved acquisitions/locations retained: {len(data['unresolved'])}.")
    for item in data['unresolved']:
        page = item.get('provenance', {}).get('physical_page', 'UNKNOWN')
        lines.append(f"- Unresolved evidence p.{page}: {item['reason']}")
    for a in data['attempts']:
        if a['status'] in {'FAILED', 'SKIPPED', 'COMPLETED_EMPTY'}:
            lines.append(f"- {a['method']} p.{a['physical_page']}: {a['status']}; {a['reason'] or 'no further evidence'}. Other representations may exist.")
    return '\n'.join(lines)+'\n'

@contextlib.contextmanager
def capture(job_id, root=None):
    rec = Recorder(job_id, root); token = _ACTIVE.set(rec)
    try: yield rec
    finally:
        _observe('persist'); _ACTIVE.reset(token)

def review_entry(kind):
    def decorate(fn):
        @functools.wraps(fn)
        def run(*args, **kwargs):
            if _ACTIVE.get() is not None: return fn(*args, **kwargs)
            job_id = str(args[0]) if kind == 'server' else 'cli-' + uuid.uuid4().hex
            with capture(job_id): return fn(*args, **kwargs)
        return run
    return decorate

def document_scope(fn):
    @functools.wraps(fn)
    def run(path, *args, **kwargs):
        if _ACTIVE.get() is None: return fn(path, *args, **kwargs)
        sid = _observe('begin_source', path); token = _SOURCE.set(sid); stage_token = _STAGE.set('document-acquisition')
        try:
            event('document-load', 'STARTED')
            result = fn(path, *args, **kwargs)
            _observe('document', sid, *result) if sid else None
            event('document-load', 'COMPLETED_WITH_RESULTS' if result[0] or result[1] else 'COMPLETED_EMPTY')
            return result
        except Exception as exc:
            event('document-load', 'FAILED', reason=type(exc).__name__ + ': ' + str(exc)); raise
        finally:
            _STAGE.reset(stage_token); _SOURCE.reset(token)
    return run

def stage(name):
    def decorate(fn):
        @functools.wraps(fn)
        def run(*args, **kwargs):
            token = _STAGE.set(name); _observe('stage_event', name, 'ENTER')
            try: return fn(*args, **kwargs)
            finally: _observe('stage_event', name, 'EXIT'); _STAGE.reset(token)
        return run
    return decorate

def acquisition(method):
    def decorate(fn):
        @functools.wraps(fn)
        def run(*args, **kwargs):
            event(method, 'STARTED')
            try: result = fn(*args, **kwargs)
            except Exception as exc:
                event(method, 'FAILED', reason=type(exc).__name__+': '+str(exc)); raise
            event(method, 'COMPLETED_WITH_RESULTS' if result else 'COMPLETED_EMPTY', reason='Returned result; completeness not established')
            return result
        return run
    return decorate

def execution(phase, value): return _observe('execution', phase, value)
def execution_totals(): return _observe('execution_totals') or {}

def media(png, page, purpose): return _observe('media', png, page, purpose)

def event(method, status, page=None, reason=None): return _observe('event', method, status, page, reason)
def request_started(endpoint, raw): return _observe('request_started', endpoint, raw)
def request_finished(ticket, raw=None, error=None): return _observe('request_finished', ticket, raw, error)

def current_status():
    rec = _ACTIVE.get()
    if rec is None: return {"state": "UNKNOWN"}
    return {"state": "AUDIT_INCOMPLETE" if rec.errors else "RECORDED" if rec.started else "NO_OBSERVATIONS",
            "errors": list(rec.errors), "directory": str(rec.directory)}

def unexamined_figures():
    """Figure labels the active ledger holds by caption only, with no image
    receipt. Reads existing ledger state; records nothing. Empty when no
    ledger is active, which means UNKNOWN, not "every figure was read"."""
    rec = _ACTIVE.get()
    if rec is None: return []
    imaged = {(m.get('source_sha256'), m.get('physical_page')) for m in rec.data.get('media', [])}
    out = []
    for obj in sorted(rec.data.get('objects', {}).values(), key=lambda o: (o.get('physical_page') or 0, o['label'])):
        if obj.get('type') != 'figure': continue
        if (obj.get('source_sha256'), obj.get('physical_page')) in imaged: continue
        label = obj['label'] + (f" (PDF p.{obj['physical_page']})" if obj.get('physical_page') else '')
        if label not in out: out.append(label)
    return out

def read_sidecar(job_id, root=None):
    directory = (Path(root) if root else storage_root()) / safe_id(job_id)
    data = json.loads((directory / 'LEDGER.json').read_text())
    def verify(value):
        if isinstance(value, dict):
            if {'file', 'sha256', 'bytes'} <= value.keys():
                if Path(value['file']).name != value['file']: raise ValueError('Invalid artifact path')
                raw = (directory / value['file']).read_bytes()
                if len(raw) != value['bytes'] or sha(raw) != value['sha256']: raise ValueError('Sidecar artifact changed')
            else:
                for v in value.values(): verify(v)
        elif isinstance(value, list):
            for v in value: verify(v)
    verify(data)
    for sid, source in data['sources'].items():
        if sid != source['sha256'] or sid != source['artifact']['sha256']: raise ValueError('Source identity changed')
    for oid, obj in data['objects'].items():
        expected = 'object-' + sha(encoded([obj['source_sha256'], obj['type'], obj['label'], obj['physical_page']]))[:24]
        if oid != obj['id'] or oid != expected or obj['source_sha256'] not in data['sources']: raise ValueError('Object identity changed')
    return data
