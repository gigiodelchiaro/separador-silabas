import json
import re
from bs4 import BeautifulSoup

def scrape_dictionary(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []
    
    table = None
    for t in soup.find_all('table'):
        if t.find('th', string='Palavra'):
            table = t
            break
    
    if not table:
        return None
        
    rows = table.find_all('tr')

    for row in rows[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) == 2:
            word_data = cols[0].get_text(strip=True)
            syllable_html_content = cols[1].decode_contents()

            # Extract word and description
            word = word_data.split('(')[0].strip()
            description = word_data.split('(')[1].replace(')', '').strip() if '(' in word_data else ''

            # Syllables
            temp_soup = BeautifulSoup(syllable_html_content, 'html.parser')
            
            syllable_string_with_dots = temp_soup.get_text()
            syllables = re.split('[·-]', syllable_string_with_dots)
            syllables = [s.strip() for s in syllables if s.strip()]
            
            # Tonic
            tonic_text = None
            uts = temp_soup.find_all('u')
            tonic_u = None

            if uts:
                # Prefer <u> with <b> inside
                for u in uts:
                    if u.find('b'):
                        tonic_u = u
                        break
                # Fallback to the last <u> if no <b> is found inside any <u>
                if not tonic_u:
                    tonic_u = uts[-1]

            if tonic_u:
                tonic_text = tonic_u.get_text(strip=True)

            tonic_index_from_start = -1
            if tonic_text:
                try:
                    tonic_index_from_start = syllables.index(tonic_text)
                except ValueError:
                    # Fallback for cases where tonic text might have extra whitespace or be a substring
                    for i, s in enumerate(syllables):
                        if tonic_text in s:
                            tonic_index_from_start = i
                            break
            
            tonic = -1
            if tonic_index_from_start != -1:
                tonic = len(syllables) - tonic_index_from_start

            data.append({
                'word': word,
                'description': description,
                'syllables': syllables,
                'tonic': tonic
            })

    return data

with open('/home/gigiodc/git/separador-silabas/Dicionário de divisão silábica.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

scraped_data = scrape_dictionary(html_content)

if scraped_data:
    with open('/home/gigiodc/git/separador-silabas/dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)
    print("Scraping complete. Data saved to dictionary.json")
else:
    print("Could not find the main table in the HTML file.")