import re

def tonic(word_separated):
    """
    Determines the tonic syllable of a word, given its separated syllables.
    The position is returned as an index from the end of the word (1-based).
    """
    if not isinstance(word_separated, list) or not word_separated:
        return None

    strong_accents = 'áéíóúàèìòùâêîôûÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ'
    weak_accents = 'ãẽĩõũÃẼĨÕŨ'

    # Check for explicitly accented syllables (strong comes first)
    for i, syllable in enumerate(reversed(word_separated)):
        if any(char in strong_accents for char in syllable):
            return i + 1
    
    for i, syllable in enumerate(reversed(word_separated)):
        if any(char in weak_accents for char in syllable):
            return i + 1

    # If no accent, apply default Portuguese grammar rules
    last_syllable = word_separated[-1]
    
    # This pattern identifies words that are typically "oxítonas" (stressed on the last syllable)
    # if they don't have an explicit accent.
    pattern = r'[iIuU]s?|[aA]is|[eE]is|[oO]is|[uU]ns|[eE]ns|[rRlLzZ]$'
    
    if re.search(pattern, last_syllable, re.IGNORECASE):
        return 1
    
    # Words ending in a hyphenated suffix like "-lo" are complex.
    # This is a simplification.
    if len(word_separated) > 1 and word_separated[-1] == 'lo':
        return 2 # Assuming the stress is on the second to last syllable

    # By default, words are "paroxítonas" (stressed on the second-to-last syllable).
    return 2