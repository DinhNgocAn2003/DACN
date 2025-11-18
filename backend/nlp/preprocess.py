import re
import unicodedata
from typing import Dict

# small abbreviation map — extend as needed
ABBREVIATIONS = {
    r"\bo\b": 'ở',
    r"\bphong\b": 'phòng',
    r"\bph\b": 'phòng',
    r"\bhop\b": 'họp',
    r"\bgap\b": 'gặp',
    r"\bnhom\b": 'nhóm',
    r"\bluc\b": 'lúc',
    r"\blk\b": 'lúc',
    r"\bhn\b": 'hà nội',
    r"\btp\b": 'thành phố',
    r"\bg\b": 'giờ',
    r"\bgio\b": 'giờ',
    r"\bh\b": 'giờ',
    r"\bpt\b": 'phút',
    r"\btoi\b": 'tối',
    r"\btrua\b": 'trưa',

}


def remove_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def expand_abbreviations(s: str) -> str:
    out = s
    for abbr_re, full in ABBREVIATIONS.items():
        out = re.sub(abbr_re, full, out, flags=re.IGNORECASE)
    return out


def normalize_text(s: str) -> Dict[str, str]:
    if not s:
        return {'raw': '', 'normalized': '', 'no_accents': ''}
    raw = s.strip()
    normalized = raw.lower()
    # basic punctuation cleanup
    normalized = re.sub(r"[\t\n\r]+", ' ', normalized)
    normalized = re.sub(r"\s+", ' ', normalized)
    # expand simple abbreviations
    normalized = expand_abbreviations(normalized)
    no_accents = remove_diacritics(normalized)
    return {'raw': raw, 'normalized': normalized, 'no_accents': no_accents}
