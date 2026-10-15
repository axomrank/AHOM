#!/usr/bin/env python3
"""
Comprehensive Assamese Personalities Dataset Builder
Integrates curated database with Wikipedia's 'List of people from Assam'
(https://en.wikipedia.org/wiki/List_of_people_from_Assam)
Outputs:
  - data/assam_personalities.csv (with 'wikipedia_url' column)
  - data/assam_personalities.json
"""

import urllib.request
import re
import csv
import json
import os
from bs4 import BeautifulSoup

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\d+\]', '', text)  # remove citation markers like [1], [2]
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_slug(name):
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

# Map Wikipedia sections to unified fields & eras
SECTION_MAPPING = {
    'Historical figures': ('Medieval / Ancient Era', 'Royalty & Historical Leadership', 'Historical Figure'),
    'Religious leaders': ('Medieval / Modern Era', 'Spiritual & Social Reform', 'Religious Leader / Reformer'),
    'Administrators, diplomats and justices': ('Modern & Contemporary Era', 'Law, Judiciary & Administration', 'Administrator / Justice / Civil Servant'),
    'Academicians and scholars': ('Modern & Contemporary Era', 'Science, Medicine & Academia', 'Academician / Scholar / Researcher'),
    'Writers': ('Modern & Contemporary Era', 'Literature & Creative Writing', 'Author / Novelist / Littérateur'),
    'Poets': ('Modern & Contemporary Era', 'Literature & Poetry', 'Poet / Lyricist'),
    'Journalists': ('Modern & Contemporary Era', 'Journalism & Media', 'Journalist / Editor / Broadcaster'),
    'Performing artists': ('Modern & Contemporary Era', 'Music, Cinema & Performing Arts', 'Performing Artist'),
    'Actors and models': ('Contemporary Era', 'Cinema & Performing Arts', 'Actor / Film & Theatre Artist'),
    'Film directors': ('Modern & Contemporary Era', 'Cinema & Filmmaking', 'Film Director / Producer'),
    'Musicians': ('Modern & Contemporary Era', 'Music & Performing Arts', 'Musician / Singer / Composer'),
    'Activists': ('Modern & Contemporary Era', 'Freedom Movement & Social Activism', 'Activist / Social Reformer'),
    'Politicians': ('Modern & Contemporary Era', 'Politics & Public Governance', 'Politician / Statesperson'),
    'Sports': ('Contemporary Era', 'Sports & Athletics', 'Athlete / Sportsperson'),
    'Archer': ('Contemporary Era', 'Sports & Athletics', 'Archer / Olympian'),
    'Athletes': ('Contemporary Era', 'Sports & Athletics', 'Track & Field Athlete'),
    'Badminton player': ('Contemporary Era', 'Sports & Athletics', 'Badminton Player'),
    'Bodybuilding': ('Contemporary Era', 'Sports & Athletics', 'Bodybuilder / Fitness Icon'),
    'Boxers': ('Contemporary Era', 'Sports & Athletics', 'Boxer / Pugilist'),
    'Cricketers': ('Contemporary Era', 'Sports & Athletics', 'Cricketer'),
    'Footballers': ('Contemporary Era', 'Sports & Athletics', 'Footballer'),
    'Gymnast': ('Contemporary Era', 'Sports & Athletics', 'Gymnast'),
    'Tennis player': ('Contemporary Era', 'Sports & Athletics', 'Tennis Player'),
    'Table tennis player': ('Contemporary Era', 'Sports & Athletics', 'Table Tennis Player'),
    'Naturalists': ('Contemporary Era', 'Environment & Wildlife Conservation', 'Naturalist / Conservationist'),
    'Others': ('Modern & Contemporary Era', 'Science, Innovation & Public Distinction', 'Innovator / Public Figure')
}

def fetch_wikipedia_people():
    url = 'https://en.wikipedia.org/wiki/List_of_people_from_Assam'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    output = soup.find('div', class_='mw-parser-output')
    sections = output.find_all('section')
    
    entries = []
    
    for sec in sections:
        h = sec.find(['h2', 'h3', 'h4'])
        sec_title = h.get_text().replace('[edit]', '').strip() if h else 'General'
        if sec_title in ['See also', 'References', 'External links', 'Notes', 'No heading']:
            continue
        
        for li in sec.find_all('li'):
            a_tags = li.find_all('a')
            wiki_link = ''
            person_name = ''
            for a in a_tags:
                href = a.get('href', '')
                if '/wiki/' in href and not any(p in href for p in ['/wiki/Help:', '/wiki/File:', '/wiki/Category:', '/wiki/Special:', '/wiki/Wikipedia:', '/wiki/Template:', '/wiki/Portal:', '/wiki/Main_Page']):
                    wiki_link = href if href.startswith('http') else ('https://en.wikipedia.org' + href)
                    person_name = a.get_text().strip()
                    break
            
            full_text = clean_text(li.get_text())
            if not person_name:
                parts = re.split(r'[,–-]', full_text)
                person_name = parts[0].strip() if parts else full_text
            
            if person_name and wiki_link:
                entries.append({
                    'section': sec_title,
                    'name': person_name,
                    'wiki_url': wiki_link,
                    'raw_text': full_text
                })
    return entries

def build_merged_dataset():
    # Load existing base records
    base_file = 'data/assam_personalities.json'
    existing_items = []
    if os.path.exists(base_file):
        with open(base_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_items = data.get('personalities', [])
            
    print(f"Loaded {len(existing_items)} existing base records.")
    
    # Map existing records by normalized name / slug
    existing_map = {}
    for item in existing_items:
        key = re.sub(r'[^a-z0-9]', '', item['name_english'].lower())
        existing_map[key] = item
        
    wiki_entries = fetch_wikipedia_people()
    print(f"Fetched {len(wiki_entries)} raw entries from Wikipedia.")
    
    # Merge and deduplicate
    unified_list = []
    processed_urls = set()
    processed_names = set()
    
    # 1. Process and update existing curated items first with exact Wikipedia URL
    for item in existing_items:
        item_slug = create_slug(item['name_english'])
        item_norm = re.sub(r'[^a-z0-9]', '', item['name_english'].lower())
        
        # Check matching wiki entry
        matched_url = ""
        for we in wiki_entries:
            we_norm = re.sub(r'[^a-z0-9]', '', we['name'].lower())
            if we_norm in item_norm or item_norm in we_norm:
                matched_url = we['wiki_url']
                break
        
        # Fallback canonical wiki link generation if not directly matched
        if not matched_url:
            clean_name_for_url = item['name_english'].split('(')[0].replace('Bharat Ratna ', '').replace('Dr. ', '').replace('Mahapurusha ', '').replace('Padmashree ', '').replace('Padmabhushan ', '').replace('Padmavibhushan ', '').replace('Birangana ', '').replace('Bir ', '').replace('Arjuna ', '').replace('Sahityarathi ', '').replace('Karmavir ', '').replace('Deshabhakta ', '').strip()
            clean_name_for_url = clean_name_for_url.replace(' ', '_')
            matched_url = f"https://en.wikipedia.org/wiki/{clean_name_for_url}"
        
        item['wikipedia_url'] = matched_url
        unified_list.append(item)
        processed_urls.add(matched_url)
        processed_names.add(item_norm)

    # 2. Integrate new entries from Wikipedia list
    new_added_count = 0
    for we in wiki_entries:
        url = we['wiki_url']
        name = we['name']
        norm_name = re.sub(r'[^a-z0-9]', '', name.lower())
        
        if url in processed_urls or norm_name in processed_names:
            continue
        
        # Determine era & field mapping
        sec = we['section']
        era_default, field_default, role_default = SECTION_MAPPING.get(sec, ('Modern & Contemporary Era', 'Public Distinction', 'Notable Personality'))
        
        # Extract achievements from raw text
        raw_text = we['raw_text']
        achievement_text = raw_text
        if ',' in raw_text:
            parts = raw_text.split(',', 1)
            if len(parts) > 1 and len(parts[1].strip()) > 5:
                achievement_text = parts[1].strip()
        
        slug_id = create_slug(name)
        
        new_item = {
            'id': slug_id,
            'name_english': name,
            'name_assamese': "",  # Populated or native
            'era': era_default,
            'approx_period': "20th – 21st Century",
            'primary_field': field_default,
            'sub_field_roles': role_default,
            'dynasty_movement_org': f"Assam / {sec}",
            'key_achievements': achievement_text,
            'notable_works_titles': f"Featured on Wikipedia: {name}",
            'region_association': "Assam",
            'gender': "Unspecified",
            'wikipedia_url': url
        }
        
        unified_list.append(new_item)
        processed_urls.add(url)
        processed_names.add(norm_name)
        new_added_count += 1
        
    print(f"Total unified personalities after Wikipedia merge: {len(unified_list)} (Added {new_added_count} new entries).")
    
    # Sort unified list logically by era and name
    era_order = {
        'Ancient / Epic Period': 1,
        'Ancient (Varman Dynasty)': 2,
        'Ancient (Mlechchha Dynasty)': 3,
        'Ancient (Pala Dynasty)': 4,
        'Ancient Period': 5,
        'Ancient / Early Medieval': 6,
        'Medieval (Ahom Dynasty)': 7,
        'Medieval (Koch Dynasty)': 8,
        'Medieval (Chutia Dynasty)': 9,
        'Medieval (Bhakti Movement)': 10,
        'Medieval (Pre-Sankarian Literature)': 11,
        'Medieval (Sankarian Literature)': 12,
        'Medieval (Kala Samhati Vaishnavism)': 13,
        'Medieval (Sufi & Cultural Harmony)': 14,
        'Medieval (Literature & Philosophy)': 15,
        'Medieval (Arts & Veterinary Science)': 16,
        'Medieval / Ancient Era': 17,
        'Colonial Renaissance': 18,
        'Colonial Renaissance (Sanskrit & Civil Service)': 19,
        'Jonaki Era (Modern Literature)': 20,
        'Colonial & Modern Literature': 21,
        'Historiography & Governance': 22,
        'Historiography & Freedom Movement': 23,
        'Linguistic Scholarship': 24,
        'Indology & Cultural Scholarship': 25,
        'Freedom Struggle': 26,
        'Freedom Struggle (Early Resistance)': 27,
        'Freedom Struggle (1857 Revolt)': 28,
        'Freedom Struggle (Quit India 1942)': 29,
        'Freedom Struggle & Literature': 30,
        'Freedom Struggle & Feminist Movement': 31,
        'Freedom Struggle & Governance': 32,
        'Freedom Struggle & Post-Independence': 33,
        'Freedom Struggle & Parliamentarian': 34,
        'National Politics & Freedom Movement': 35,
        'Post-Independence Governance': 36,
        'Modern Era': 37,
        'Modern Era (Arts, Revolution & Culture)': 38,
        'Modern Era (Cinema, Music & Drama)': 39,
        'Modern Era (Theatre & Cinema)': 40,
        'Modern Era (Lyric Poetry & Music)': 41,
        'Modern & Contemporary (Folk Music)': 42,
        'Modern & Contemporary (Folk & Bihu Music)': 43,
        'Modern & Contemporary (Music & Cinema)': 44,
        'Modern Literature': 45,
        'Modern Literature & Journalism': 46,
        'Modern Literature & Folkloristics': 47,
        'Modern Cinema, Literature & Journalism': 48,
        'Journalism & Sports Architecture': 49,
        'Science & Space Exploration': 50,
        'Science & Meteorology': 51,
        'Mathematics & Statistics': 52,
        'Grassroots Innovation & Technology': 53,
        'Science & Plasma Physics': 54,
        'Astrophysics & Academia': 55,
        'Healthcare & Medicine': 56,
        'Environmental Leadership': 57,
        'Wildlife Conservation': 58,
        'Wildlife Documentary & Conservation': 59,
        'Sports (Football & Olympic Captain)': 60,
        'Sports (Athletics)': 61,
        'Sports (Table Tennis)': 62,
        'Sports (Badminton)': 63,
        'Sports (Archery)': 64,
        'Contemporary Era': 65,
        'Contemporary (Music)': 66,
        'Contemporary (Music & Cinema)': 67,
        'Contemporary (Cinema & Theatre)': 68,
        'Contemporary (Cinema & International Theatre)': 69,
        'Contemporary (Independent Cinema)': 70,
        'Contemporary Cinema': 71,
        'Contemporary Literature': 72,
        'Contemporary Literature & Journalism': 73,
        'Contemporary Sports (Athletics)': 74,
        'Contemporary Sports (Boxing)': 75,
        'Contemporary Sports (Cricket)': 76,
        'Modern & Contemporary Era': 77
    }
    
    unified_list.sort(key=lambda x: (era_order.get(x['era'], 99), x['name_english']))
    
    # 3. Export CSV
    csv_file = 'data/assam_personalities.csv'
    headers = [
        'id', 'name_english', 'name_assamese', 'era', 'approx_period',
        'primary_field', 'sub_field_roles', 'dynasty_movement_org',
        'key_achievements', 'notable_works_titles', 'region_association',
        'gender', 'wikipedia_url'
    ]
    
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for p in unified_list:
            writer.writerow(p)
            
    print(f"✅ Successfully wrote {len(unified_list)} rows to {csv_file}")
    
    # 4. Export JSON
    json_file = 'data/assam_personalities.json'
    dataset = {
        'title': 'Eminent Personalities of Assam: Ancient to Present',
        'description': 'A comprehensive, structured dataset of notable historical, cultural, scientific, literary, political, and sports figures of Assam with Wikipedia citations.',
        'sourceReference': 'https://en.wikipedia.org/wiki/List_of_people_from_Assam',
        'totalCount': len(unified_list),
        'erasCovered': sorted(list(set(p['era'] for p in unified_list))),
        'fieldsCovered': sorted(list(set(p['primary_field'] for p in unified_list))),
        'personalities': unified_list
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Successfully wrote {len(unified_list)} items to {json_file}")

if __name__ == '__main__':
    build_merged_dataset()
