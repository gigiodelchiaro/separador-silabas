import json
import re
import requests
import string
from bs4 import BeautifulSoup

import json
import re
import requests
import string
from bs4 import BeautifulSoup

BASE_URL = "http://www.portaldalinguaportuguesa.org/index.php?action=syllables&act=list&letter="

# --- TEST MODE CONFIGURATION ---
TEST_MODE = False # Set to True to scrape only a limited number of pages per letter for testing
MAX_PAGES_PER_LETTER = 1 # Number of pages to scrape per letter in test mode
# -------------------------------

def scrape_dictionary(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []
    
    table = None
    # Find the table that contains the text "Palavra" and "Divisão silábica"
    for t in soup.find_all('table'):
        if "Palavra" in t.get_text() and "Divisão silábica" in t.get_text():
            table = t
            break
    
    if not table:
        print("Debug: Table not found in HTML content.")
        return None
        
    rows = table.find_all('tr')
    print(f"Debug: Found {len(rows) - 1} data rows in table.")

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

all_scraped_data = []

for letter in string.ascii_lowercase:
    start_index = 0
    page_count = 0
    while True:
        url = f"{BASE_URL}{letter}&start={start_index}"
        print(f"Scraping {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} for {url}")
            print(f"Response content: {response.text[:500]}...") # Print first 500 chars of content
            break # Exit loop for this letter if there's an error
        html_content = response.text
        
        scraped_data = scrape_dictionary(html_content)
        if scraped_data:
            all_scraped_data.extend(scraped_data)
            print(f"Debug: Scraped {len(scraped_data)} items from {url}")
        else:
            print(f"Debug: No data scraped from {url}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        next_page_link = soup.find('a', string='seguintes')
        
        page_count += 1
        if TEST_MODE and page_count >= MAX_PAGES_PER_LETTER:
            print(f"Debug: Test mode enabled. Breaking after {MAX_PAGES_PER_LETTER} page(s) for letter '{letter}'.")
            break

        if next_page_link:
            start_index += 100
            print(f"Debug: Found 'seguintes' link. Next start_index: {start_index}")
        else:
            print(f"Debug: No 'seguintes' link found. Breaking loop for letter '{letter}'.")
            break

if all_scraped_data:
    with open('/home/gigiodc/git/separador-silabas/dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(all_scraped_data, f, ensure_ascii=False, indent=4)
    print("Scraping complete. Data saved to dictionary.json")
else:
    print("No data scraped.")