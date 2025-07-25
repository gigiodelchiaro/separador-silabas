import json
import re
import sys
import os

def load_rules(file_path):
    """Loads the rules from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def prepare_patterns(rules):
    """Prepares patterns by substituting placeholders."""
    vogais = rules["vogais_fortes"] + rules["vogais_fracas"]
    consoantes = rules["consoantes_fortes"] + rules["consoantes_nasais"] + rules["consoantes_s"] + rules["consoantes_l_r"]
    letras = vogais + consoantes
    digrafos = rules["digrafos"]
    divisor = "-"

    for pattern in rules["padroes"]:
        p_regex = pattern["regex"]
        p_regex = p_regex.replace("{divisor}", divisor)
        p_regex = p_regex.replace("{\\1}", r"\1")
        p_regex = p_regex.replace("{\1}", r"\1")
        p_regex = p_regex.replace("{\\2}", r"\2")
        p_regex = p_regex.replace("{\\3}", r"\3")
        p_regex = p_regex.replace("{\\w}", r"\w")
        p_regex = p_regex.replace("{\\s}", r"\s")
        p_regex = p_regex.replace("{consoantes_fortes}", re.escape(rules["consoantes_fortes"]))
        p_regex = p_regex.replace("{consoantes_l_r}", re.escape(rules["consoantes_l_r"]))
        p_regex = p_regex.replace("{consoantes_s}", re.escape(rules["consoantes_s"]))
        p_regex = p_regex.replace("{consoantes_nasais}", re.escape(rules["consoantes_nasais"]))
        p_regex = p_regex.replace("{vogais}", re.escape(vogais))
        p_regex = p_regex.replace("{vogais_fortes}", re.escape(rules["vogais_fortes"]))
        p_regex = p_regex.replace("{digrafos}", digrafos)
        p_regex = p_regex.replace("{letras}", re.escape(letras))
        pattern["regex"] = p_regex

        p_sub = pattern["sub"]
        p_sub = p_sub.replace("{divisor}", divisor)
        p_sub = p_sub.replace("{\\1}", r"\1")
        p_sub = p_sub.replace("{\1}", r"\1")
        p_sub = p_sub.replace("{\\2}", r"\2")
        p_sub = p_sub.replace("{\\3}", r"\3")
        p_sub = p_sub.replace("{\\w}", r"\w")
        p_sub = p_sub.replace("{\\s}", r"\s")
        pattern["sub"] = p_sub

    return rules

def apply_rules(text, rules):
    """Applies rules to the given text."""
    for pattern in rules["padroes"]:
        text = re.sub(pattern["regex"], pattern["sub"], text)
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python syllable.py <word>")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    rules_file = os.path.join(script_dir, "rules.json")

    rules = load_rules(rules_file)
    rules = prepare_patterns(rules)

    input_text = " " + sys.argv[1]
    output_text = apply_rules(input_text, rules)

    print(output_text.strip().replace("@", "-"))
