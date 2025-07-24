import re

def syllabify_pt_br(word: str) -> str:
    """
    Separates a Portuguese word into syllables based on the official rules.
    This version uses a robust iterative approach to fix previous errors.

    Args:
        word: The Portuguese word to be syllabified.

    Returns:
        A string with the word's syllables separated by hyphens.
    """
    if not isinstance(word, str) or not word:
        return ""

    word = word.lower()
    
    # Rule: Replace indivisible units with placeholders. This is the most reliable way
    # to handle them as single consonants in the logic.
    replacements = {
        'ch': '\x01', 'lh': '\x02', 'nh': '\x03',
        'gu': '\x04', 'qu': '\x05', 'rr': '\x06', 'ss': '\x07'
    }
    for original, temp in replacements.items():
        word = word.replace(original, temp)

    vowels = "aáàâãeéêiíîoóôõuúû"
    consonants = "bcdfghjklmnpqrstvwxyz\x01\x02\x03\x04\x05" # rr/ss are handled separately
    clusters = ('bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'tl', 'tr', 'vr')

    syllables = []
    i = 0
    while i < len(word):
        current_syllable = ""
        # 1. Find the beginning of the syllable (consonant part - ONSET)
        onset_end = i
        while onset_end < len(word) and word[onset_end] not in vowels:
            onset_end += 1
        current_syllable += word[i:onset_end]

        # 2. Find the vowel part (NUCLEUS)
        nucleus_end = onset_end
        while nucleus_end < len(word) and word[nucleus_end] in vowels:
            nucleus_end += 1
        current_syllable += word[onset_end:nucleus_end]

        # 3. Look ahead to find the Coda and the split point
        coda_end = nucleus_end
        if coda_end >= len(word): # Word ends in a vowel
            syllables.append(current_syllable)
            break

        # Peek at what follows the vowel nucleus
        next1 = word[coda_end] if coda_end < len(word) else None
        next2 = word[coda_end + 1] if coda_end + 1 < len(word) else None
        
        # Rule: Word ends in a consonant (e.g., devagar, mulher)
        if next2 is None:
            current_syllable += next1
            coda_end += 1
            
        # Rule: V-C-V pattern (e.g., ca-sa). Split before the C. No coda.
        elif next1 in consonants and next2 in vowels:
            pass # Coda is empty, syllable ends at nucleus_end

        # Rule: V-C-C pattern (e.g., car-ro, pers-pectiva, a-tle-ta)
        elif next1 in consonants and next2 in consonants:
            # If C-C is an indivisible cluster, split before it. No coda.
            if f"{next1}{next2}" in clusters:
                pass # Coda is empty
            # Otherwise, the first consonant is the coda. Split after it.
            else:
                current_syllable += next1
                coda_end += 1

        # Rule: Handle double consonants 'rr' and 'ss' which must be split
        elif next1 == '\x06': # rr
            current_syllable += 'r'
            coda_end += 1
        elif next1 == '\x07': # ss
            current_syllable += 's'
            coda_end += 1
            
        syllables.append(current_syllable)
        i = coda_end

    # Join the syllables and restore the original digraphs
    result = "-".join(filter(None, syllables))
    for original, temp in replacements.items():
        if temp in ('\x06', '\x07'): # Handle rr, ss
             result = result.replace(temp, original[0])
        else:
             result = result.replace(temp, original)

    return result

# --- Main execution block ---
words_to_test = [
    "devagar",      # Expected: de-va-gar
    "fluidez",      # Expected: flu-i-dez
    "sublime",      # Expected: su-bli-me
    "perspectiva",  # Expected: pers-pec-ti-va
    "plano",        # Expected: pla-no
    "coordenar",    # Expected: co-or-de-nar
    "psicólogo",    # Expected: psi-có-lo-go
    "carro",        # Expected: car-ro
    "pêssego",      # Expected: pês-se-go
    "ninho",        # Expected: ni-nho
    "palha",        # Expected: pa-lha
    "queijo",       # Expected: quei-jo
    "guitarra",     # Expected: gui-tar-ra
    "saúde",        # Expected: sa-ú-de
    "apto",         # Expected: ap-to
    "atleta"        # Expected: a-tle-ta
]

print("Syllable Separation Results (Final Corrected Version):")
for word in words_to_test:
    print(f"{word.ljust(15)} -> {syllabify_pt_br(word)}")