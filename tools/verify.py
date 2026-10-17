#!/usr/bin/env python3
"""Validate the canonical, hand-maintained demo. Requires beancount and beanquery."""
import json
import re
import subprocess
import sys
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
from beancount import loader
from beancount.core import data

ROOT = Path(__file__).resolve().parents[1]
entries, errors, _ = loader.load_file(str(ROOT / 'main.bean'))
if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)
transactions = [e for e in entries if isinstance(e, data.Transaction)]
classic = [t for t in transactions if 'demo-classic' in t.tags]
assert len(classic) == 14, f'Expected 14 classic examples, got {len(classic)}'

def account_total(txns, prefix, currency='CNY'):
    return sum((p.units.number for t in txns for p in t.postings
                if p.account.startswith(prefix) and p.units.currency == currency), Decimal(0))

refund = [t for t in classic if 'refund-uniqlo-20261016' in t.links]
assert len(refund) == 3
assert account_total(refund, 'Expenses:Shopping:Clothing') == Decimal('400')
reimburse = [t for t in classic if 'reimburse-shili-20261017' in t.links]
assert len(reimburse) == 4
assert account_total(reimburse, 'Assets:Receivable:Reimbursement') == 0
people = defaultdict(Decimal)
for t in transactions:
    for p in t.postings:
        if p.account == 'Assets:Receivable:Personal':
            people[(p.meta or {}).get('person')] += p.units.number
assert people['小陈'] == Decimal('60')
assert people['小林'] == Decimal('160')
config = json.loads((ROOT / 'ledger-x.json').read_text())
assert config['default_currency'] == 'CNY'
assert any(s['query'] == '#demo-classic' for s in config['searches'])
# Run both query directives and the standalone BQL with the official query engine.
queries = [e.query_string for e in entries if isinstance(e, data.Query)]
text = (ROOT / 'queries/reports.bql').read_text()
queries += [part.strip() for part in re.split(r'^--[^\n]*\n', text, flags=re.M) if part.strip()]
for query in queries:
    subprocess.run([str(Path(sys.executable).with_name('bean-query')), str(ROOT / 'main.bean'), query], check=True, stdout=subprocess.DEVNULL)
print(f'OK: {len(transactions)} transactions, {len(classic)} classic examples, {len(queries)} queries; refund, reimbursement and personal balances verified.')
