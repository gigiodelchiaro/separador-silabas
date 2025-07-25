import os
import json
import glob
from bs4 import BeautifulSoup
import logging

# Configure basic logging to show progress and potential issues
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_word_data_from_row(row):
    """
    Extracts word, description, syllables, and tonic position from a table row.
    """
    cells = row.find_all('td')
    if len(cells) != 2:
        return None

    # --- Extract word and description ---
    word_cell = cells[0]
    word_tag = word_cell.find('b')
    if not word_tag:
        return None
    word = word_tag.get_text(strip=True)

    full_text = word_cell.get_text(strip=True)
    description = ""
    if '(' in full_text and ')' in full_text:
        start = full_text.find('(')
        end = full_text.find(')')
        description = full_text[start + 1:end]

    # --- Extract syllables and tonic ---
    syllable_cell = cells[1]
    syllable_string = syllable_cell.get_text(strip=True).replace('·', '-')
    syllables = [s.strip() for s in syllable_string.split('-') if s.strip()]

    tonic_position = -1
    tonic_text = None
    u_tags = syllable_cell.find_all('u')

    if len(u_tags) == 1:
        tonic_text = u_tags[0].get_text(strip=True)
    elif len(u_tags) > 1:
        for u in u_tags:
            if u.find('b'):
                tonic_text = u.get_text(strip=True)
                break
        if not tonic_text and u_tags:
            tonic_text = u_tags[-1].get_text(strip=True)

    if tonic_text:
        try:
            # Clean tonic_text just in case
            cleaned_tonic_text = tonic_text.replace('-', '').strip()
            # Find matching syllable
            for i, syllable in enumerate(syllables):
                if cleaned_tonic_text in syllable:
                    tonic_position = len(syllables) - i
                    break
        except ValueError:
            tonic_position = -1

    return {
        "word": word,
        "description": description,
        "syllables": syllables,
        "tonic": tonic_position
    }

def find_data_table(soup):
    """Finds the specific table containing the word data by looking for its header."""
    all_tables = soup.find_all('table') # Find all tables
    for table in all_tables:
        header = table.find('tr')
        if header:
            th_elements = header.find_all('th')
            if len(th_elements) >= 2:
                header_texts = [th.get_text(strip=True) for th in th_elements]
                if 'Palavra' in header_texts[0] and 'Divisão silábica' in header_texts[1]:
                    return table
    return None

def parse_html_file(file_path):
    """
    Parses a single HTML file and extracts all word data from it.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logging.error(f"Could not read file {file_path}: {e}")
        return []

    soup = BeautifulSoup(content, 'lxml')
    
    data_table = find_data_table(soup)
    
    if not data_table:
        logging.warning(f"Could not find the main data table in {file_path}")
        return []

    rows = data_table.find_all('tr')
    
    word_list = []
    # Skip the header row
    for row in rows[1:]:
        word_data = extract_word_data_from_row(row)
        if word_data:
            word_list.append(word_data)
            
    return word_list

def main():
    """
    Main function to find and parse the specified HTML files and save the result.
    """
    html_dir = 'html'
    output_file = 'dictionary.json'
    
    if not os.path.isdir(html_dir):
        logging.error(f"Directory not found: {html_dir}")
        return

    # Process all html files in the directory
    html_files = glob.glob(os.path.join(html_dir, '**', '*.html'), recursive=True)
    
    if not html_files:
        logging.warning(f"No HTML files found in {html_dir}")
        return

    logging.info(f"Found {len(html_files)} HTML files to parse.")
    
    all_words = []
    for file_path in sorted(html_files):
        logging.info(f"Parsing {file_path}...")
        words_from_file = parse_html_file(file_path)
        if not words_from_file:
            logging.warning(f"No words extracted from {file_path}")
        all_words.extend(words_from_file)

    logging.info(f"Total words extracted: {len(all_words)}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_words, f, ensure_ascii=False, indent=4)
        logging.info(f"Successfully created {output_file} with {len(all_words)} words.")
    except Exception as e:
        logging.error(f"Could not write to {output_file}: {e}")

if __name__ == '__main__':
    main()