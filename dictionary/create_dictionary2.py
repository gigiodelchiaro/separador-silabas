import json
import re
from collections import defaultdict

def extract_words_from_bible(bible_data):
    """Extract all unique words from the Bible text"""
    words = set()
    
    # Process both testaments
    for testament in [bible_data.get('antigoTestamento', []), bible_data.get('novoTestamento', [])]:
        for book in testament:
            for chapter in book.get('capitulos', []):
                for verse in chapter.get('versiculos', []):
                    text = verse.get('texto', '')
                    # Extract words using regex (removes punctuation and splits by whitespace)
                    verse_words = re.findall(r'\b[a-zA-ZáéíóúâêîôûãõçàèìòùäëïöüÁÉÍÓÚÂÊÎÔÛÃÕÇÀÈÌÒÙÄËÏÖÜ\-]+\b', text.lower())
                    words.update(verse_words)
    
    return words

def filter_dictionary_by_bible_words(dictionary_data, bible_words):
    """Filter dictionary to only include words that appear in the Bible"""
    filtered_dictionary = []
    
    for word_entry in dictionary_data:
        word = word_entry.get('word', '').lower()
        if word in bible_words:
            filtered_dictionary.append(word_entry)
    
    return filtered_dictionary

def main():
    # Load the Bible JSON file
    try:
        with open('bible.json', 'r', encoding='utf-8') as bible_file:
            bible_data = json.load(bible_file)
    except FileNotFoundError:
        print("Error: bible.json file not found!")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in bible.json!")
        return
    
    # Load the dictionary JSON file
    try:
        with open('dictionary.json', 'r', encoding='utf-8') as dict_file:
            dictionary_data = json.load(dict_file)
    except FileNotFoundError:
        print("Error: dictionary.json file not found!")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in dictionary.json!")
        return
    
    # Extract words from Bible
    print("Extracting words from Bible...")
    bible_words = extract_words_from_bible(bible_data)
    print(f"Found {len(bible_words)} unique words in the Bible")
    
    # Filter dictionary
    print("Filtering dictionary...")
    filtered_dictionary = filter_dictionary_by_bible_words(dictionary_data, bible_words)
    print(f"Filtered dictionary contains {len(filtered_dictionary)} entries")
    
    # Save the filtered dictionary to a new JSON file
    try:
        with open('filtered_dictionary.json', 'w', encoding='utf-8') as output_file:
            json.dump(filtered_dictionary, output_file, ensure_ascii=False, indent=2)
        print("Filtered dictionary saved to 'filtered_dictionary.json'")
    except Exception as e:
        print(f"Error saving filtered dictionary: {e}")
    
    # Optional: Show some statistics
    print("\n--- Statistics ---")
    print(f"Original dictionary entries: {len(dictionary_data)}")
    print(f"Filtered dictionary entries: {len(filtered_dictionary)}")
    print(f"Reduction: {len(dictionary_data) - len(filtered_dictionary)} entries removed")

if __name__ == "__main__":
    main()