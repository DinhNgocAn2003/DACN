import sys
import os
from datetime import datetime

# ensure backend path
HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from nlp_processor import NLPProcessor
from nlp.preprocess import remove_diacritics


def test_abbreviation_and_no_diacritics():
    proc = NLPProcessor()
    text = 'gap nhom luc 14h o phong hop 301'
    res = proc.process_text(text)
    assert res.get('success') is True
    # event name should include gap/nhom after normalization
    name_no = remove_diacritics(res.get('event_name', '').lower())
    assert 'gap' in name_no or 'nhom' in name_no
    # location should be present and include 'phong' and number
    loc = res.get('location') or ''
    loc_no = remove_diacritics(loc.lower())
    assert 'phong' in loc_no
    assert '301' in loc_no


def test_all_day_event_sets_start_and_end():
    proc = NLPProcessor()
    text = 'Sinh nhật mẹ vào 10/11, cả ngày'
    res = proc.process_text(text)
    assert res.get('success') is True
    start = res.get('start_time')
    end = res.get('end_time')
    assert start is not None
    assert end is not None
    s_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    e_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    assert s_dt.hour == 0 and s_dt.minute == 0
    assert e_dt.hour == 23 and e_dt.minute == 59 and e_dt.second == 59
