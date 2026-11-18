"""Shared display wording for cards and Markdown; stored assessments stay untouched."""
import re

CHECK_QUALIFICATION = ('These checks are suggested by the AI. Consider whether their assumptions '
                       'are appropriate before relying on them.')
EXPLANATION_QUALIFICATION = ('These explanations reflect the AI’s interpretation. Check any claims '
                             'about missing information against the manuscript.')


def check_parts(check):
    """Recognise explicit list markers, never split prose into inferred checks."""
    marker = re.compile(r'^\s*(?:[-*•]\s+|\d+[.)]\s+)(.*)$')
    lines = check.strip().splitlines()
    if not any(marker.match(line) for line in lines):
        return check, []
    items, lead = [], []
    for line in lines:
        match = marker.match(line)
        if match:
            items.append(match.group(1))
        elif items:
            items[-1] += '\n' + line
        else:
            lead.append(line)
    return '\n'.join(lead), items


DISPUTED_VERDICTS = ('correct', 'reject')


def disputed(card):
    """True when the AI verifier proposed a correction to, or objected to, the
    item, whether or not its note could be shown. A flag for the reviewer's
    attention only: the item is not judged and nothing is changed."""
    prov = card.get('provenance') or {}
    return (prov.get('model_verdict') in DISPUTED_VERDICTS
            and prov.get('application_action') != 'merged_into')


def context_items(card):
    """Translate labels only; keep original AI explanations available in audit details."""
    prefixes = {
        'Verifier on the factual premise (unverified): ': 'Why the AI raised this finding: ',
        'Verifier on the inference (unverified): ': 'What the AI concludes: ',
        'Verifier on author acknowledgement (unverified): ': 'Does the manuscript acknowledge this issue? AI assessment: ',
        "Verifier's proposed correction (unverified): ": 'Suggested correction from the AI: ',
        'Point the verifier says remains (unverified): ': 'What the AI considers unresolved: ',
        "Verifier's objection (unverified): ": 'Why the AI questions this finding: ',
        'Verifier could not settle it (unverified): ': 'What the AI could not resolve: ',
        'Application note: ': 'Evidence-check limitation: ',
    }
    items = []
    for value in (card.get('established') or []) + (card.get('uncertain') or []):
        for prefix, label in prefixes.items():
            if value.startswith(prefix):
                text = label + value[len(prefix):]
                break
        else:
            if value.startswith(('The manuscript contains the ', 'What the passages mean for the item ',
                                 "Whether the evidence justifies the item's methodological conclusion ",
                                 'A quotation (')):
                continue
            text = value
        if text not in items:
            items.append(text)
    # A correction or objection is shown in the appraisal only when its
    # quotation was located. When it was not, the reviewer would otherwise
    # see only "not settled" and never learn that the verifier disputed the
    # item. Shown here, labelled as unconfirmed; the stored record and the
    # appraisal text are unchanged.
    prov = card.get('provenance') or {}
    if disputed(card) and prov.get('application_action') not in ('kept_corrected', 'kept_disputed'):
        note = (prov.get('model_correction') or prov.get('model_reason') or '').strip()
        if note:
            text = ('The AI verifier disputed this finding, but its note is not shown in the '
                    'appraisal because its supporting quotation could not be located: ' + note)
            if text not in items:
                items.append(text)
    return items


def authentication_message(card):
    """Describe recorded matching results without rechecking or changing them."""
    groups = card.get('evidence_groups') or {}
    located = sum(len(groups.get(key) or []) for key in ('supporting', 'qualifying', 'other'))
    notice = card.get('quotation_notice')
    if notice:
        if located:
            count = f'{located} additional passages were' if located != 1 else 'One additional passage was'
            return ('The main quotation supplied by the AI could not be located as an exact passage in '
                    f'the manuscript. {count} located and '
                    + ('are' if located != 1 else 'is')
                    + ' shown below. Please assess whether ' + ('they support' if located != 1 else 'it supports')
                    + ' the finding.')
        return ('The quotations supplied by the AI could not be located as exact passages in the '
                'manuscript. Please check the finding against the original manuscript.')
    if groups.get('unverified'):
        if located:
            return ('Some quotations supplied by the AI could not be located as exact passages in the '
                    'manuscript. The located passages are shown below; please assess whether they support the finding.')
        return ('The quotations supplied by the AI could not be located as exact passages in the '
                'manuscript. Please check the finding against the original manuscript.')
    return None


def material_warnings(card):
    """Deduplicate identical notices only; retain every distinct material warning."""
    seen = {(card.get('quotation_notice') or {}).get('detail')}
    warnings = []
    for warning in card.get('warnings') or []:
        detail = warning.get('detail')
        if detail and detail not in seen:
            warnings.append(warning)
            seen.add(detail)
    return warnings


def markdown_html(text):
    """Render ordinary generated Markdown through fixed tags and escaped text.

    Deliberately excludes raw HTML/images: manuscript text is untrusted. This is
    display-only; original findings, evidence bindings and exports are untouched.
    """
    import html

    def inline(value):
        tokens = []

        def code(match):
            tokens.append('<code>' + html.escape(match[1], quote=True) + '</code>')
            return '\x00' + str(len(tokens) - 1) + '\x00'

        value = re.sub(r'`([^`]+)`', code, value.replace('\x00', ''))
        value = html.escape(value, quote=True)
        value = re.sub(r'\*\*([^*]+)\*\*|__([^_]+)__',
                       lambda m: '<strong>' + (m[1] or m[2]) + '</strong>', value)
        value = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', value)
        value = re.sub(r'(?<!\w)_([^_\n]+)_(?!\w)', r'<em>\1</em>', value)
        return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m[1])], value)

    lines = str(text or '').splitlines()
    result, i = [], 0
    marker = re.compile(r'^\s*(?:(?P<ul>[-*+•])\s+|(?P<ol>\d+)[.)]\s+)(.*)$')
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        if lines[i].startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            i += 1
            result.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
            continue
        match = marker.match(lines[i])
        if match:
            tag = 'ol' if match['ol'] else 'ul'
            items = []
            while i < len(lines):
                match = marker.match(lines[i])
                if not match or ('ol' if match['ol'] else 'ul') != tag:
                    break
                item = [match[3]]
                i += 1
                while i < len(lines) and lines[i].strip() and not marker.match(lines[i]) and not lines[i].startswith('>'):
                    item.append(lines[i])
                    i += 1
                items.append('<li>' + inline('\n'.join(item)).replace('\n', '<br>') + '</li>')
            result.append('<' + tag + '>' + ''.join(items) + '</' + tag + '>')
            continue
        if lines[i].startswith('>'):
            quote = []
            while i < len(lines) and lines[i].startswith('>'):
                quote.append(re.sub(r'^> ?', '', lines[i]))
                i += 1
            result.append('<blockquote>' + inline('\n'.join(quote)).replace('\n', '<br>') + '</blockquote>')
            continue
        paragraph = [lines[i]]
        i += 1
        while i < len(lines) and lines[i].strip() and not marker.match(lines[i]) and not lines[i].startswith(('>', '```')):
            paragraph.append(lines[i])
            i += 1
        result.append('<p>' + inline('\n'.join(paragraph)).replace('\n', '<br>') + '</p>')
    return ''.join(result)
