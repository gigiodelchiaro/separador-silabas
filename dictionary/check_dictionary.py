

import json
import re

def get_bible_words():
    with open('bibliaAveMaria.json', 'r', encoding='utf-8') as f:
        bible = json.load(f)
    
    words = set()
    for testament in bible.values():
        for book in testament:
            for chapter in book['capitulos']:
                for verse in chapter['versiculos']:
                    text = verse['texto']
                    # Normalize and split into words
                    words.update(re.findall(r'\b\w+\b', text.lower()))
    return words

def get_dictionary_words():
    with open('dictionary.json', 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    
    return {entry['word'].lower() for entry in dictionary}

def main():
    bible_words = get_bible_words()
    dictionary_words = get_dictionary_words()
    
    unavailable_words = sorted(list(bible_words - dictionary_words))
    
    total_bible_words = len(bible_words)
    available_words_count = total_bible_words - len(unavailable_words)
    
    availability_percentage = (available_words_count / total_bible_words) * 100 if total_bible_words > 0 else 0
    
    print("Unavailable words:")
    for word in unavailable_words:
        print(word)
        
    print(f"\nAvailability: {availability_percentage:.2f}%")

if __name__ == "__main__":
    main()

