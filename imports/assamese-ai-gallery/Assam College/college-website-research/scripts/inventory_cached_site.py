#!/usr/bin/env python3
"""Inventory relevant links from cached college pages; never assert offerings."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

DEPARTMENT = re.compile(r'\bdepartment\b|/data/department/|department\.php', re.I)
STAFF = re.compile(r'faculty|teaching[ -]?staff|teachers?|profiles?', re.I)
ACADEMIC = re.compile(r'prospectus|admission|courses? offered|programmes? offered|academics?', re.I)
EXCLUDE = re.compile(r'merit[ -]?list|shortlisted|recruitment|advertisement|non[ -]?teaching|retired|ex[ -]?faculty', re.I)


def inventory(manifest, cache_dir):
    m = json.loads(manifest.read_text(encoding='utf-8'))
    seen = set()
    out = {'id': str(m['id']), 'college': m['college'], 'cached_pages': len(m.get('pages', [])),
           'links': {'departments': [], 'faculty': [], 'academics': []}}
    for page in m.get('pages', []):
        path = cache_dir / page.get('cache', '')
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        stream = ''
        for link in data.get('links', []):
            label = re.sub(r'\s+', ' ', link.get('label', '')).strip()
            url = link.get('url', '')
            if label.lower() in ('arts', 'science', 'commerce'):
                stream = label.title()
            if not url or not label or len(label) > 80 or EXCLUDE.search(label + ' ' + url):
                continue
            if '/#' in url or url.endswith('/#content'):
                continue
            key = (label.casefold(), url)
            if key in seen:
                continue
            seen.add(key)
            entry = {'label': label, 'url': url, 'found_on': page['url']}
            if (DEPARTMENT.search(label) and label.lower() != 'departments') or (
                DEPARTMENT.search(url) and url.rstrip('/') != page['url'].rstrip('/')
                and label.lower() not in ('home', 'about', 'academics', 'science', 'arts', 'commerce', 'departments')
            ):
                if stream:
                    entry['menu_stream'] = stream
                out['links']['departments'].append(entry)
            elif STAFF.search(label + ' ' + url):
                out['links']['faculty'].append(entry)
            elif ACADEMIC.search(label + ' ' + url):
                out['links']['academics'].append(entry)
    return out


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--cache-dir', type=Path, required=True)
    a.add_argument('--college-id', help='Directory row ID; omit for a directory-wide summary')
    a.add_argument('--all-json', action='store_true', help='Emit navigation candidates for every college')
    args = a.parse_args()
    if args.college_id:
        p = args.cache_dir / f'college_{args.college_id}.json'
        print(json.dumps(inventory(p, args.cache_dir), ensure_ascii=False, indent=2))
    else:
        manifests = sorted(args.cache_dir.glob('college_*.json'))
        totals = Counter()
        all_items = []
        for p in manifests:
            try:
                item = inventory(p, args.cache_dir)
            except (KeyError, ValueError):
                continue
            totals['colleges'] += 1
            if args.all_json:
                all_items.append(item)
            for key, links in item['links'].items():
                totals[key + '_links'] += len(links)
                totals['colleges_with_' + key] += bool(links)
        print(json.dumps(all_items if args.all_json else dict(totals), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
