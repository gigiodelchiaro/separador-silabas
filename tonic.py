import re

strong_accents = 'áéíóúàèìòùâêîôûÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ'
weak_accents = 'ãẽĩõũÃẼĨÕŨ'
def tonic(word_separated):
    if len(word_separated) == 1:
        return 1
    for i, syllable in enumerate(reversed(word_separated), start=1):
        if any(char in strong_accents for char in syllable):
            return i
    for i, syllable in enumerate(reversed(word_separated), start=1):
        if any(char in weak_accents for char in syllable):
            return i
    
    last_syllable = word_separated[-1]
    hyphen_count = last_syllable.count('-')
    last_syllable_before_hyphen = word_separated[-1-hyphen_count] if hyphen_count > 0 else ''
    pattern = r'(i(s)?|u|z|im|us|r|l|x|n|um(s)?|ps|om|on(s)?)(\W+)?$'
    
    if re.search(pattern, last_syllable):
        return 1
    elif hyphen_count > 0 and re.search(pattern, last_syllable_before_hyphen):
        return hyphen_count + 1
    return 2