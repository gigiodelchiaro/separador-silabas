import json
import re

def load_rules(file_path):
    """Loads the rules from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def prepare_patterns(rules):
    """Prepares patterns by substituting placeholders."""
    vogais = rules["vogais_fortes"] + rules["vogais_fracas"]
    consoantes = rules["consoantes_fortes"] + rules["consoantes_nasais"] + rules["consoantes_s"] + rules["consoantes_l_r"]
    letras = vogais + consoantes
    digrafos = rules["digrafos"]  # Escape digraphs
    divisor = "-"
    for pattern in rules["padroes"]:
        # Replace placeholders in regex
        pattern["regex"] = (pattern["regex"]
            .replace("{divisor}", divisor)
            .replace("{\\\\1}", r"\1")  # Correct group reference
            .replace("{\\1}", r"\1")  # Correct group reference
            .replace("{\\2}", r"\2")  # Correct group reference
            .replace("{\\3}", r"\3")  # Correct group reference
            .replace("{\\w}", r"\w")  # Correct group reference
            .replace("{\\s}", r"\s")  # Correct group reference
            .format(
            consoantes_fortes=re.escape(rules["consoantes_fortes"]),
            consoantes_l_r=re.escape(rules["consoantes_l_r"]),
            consoantes_s=re.escape(rules["consoantes_s"]),
            consoantes_nasais=re.escape(rules["consoantes_nasais"]),
            vogais=re.escape(vogais),
            vogais_fortes=re.escape(rules["vogais_fortes"]),
            digrafos=digrafos,
            divisor=divisor,
            letras=re.escape(letras)
        ))
        # Replace placeholders in replacement string
        pattern["sub"] = (
            pattern["sub"]
            .replace("{divisor}", divisor)
            .replace("{\\\\1}", r"\1")  # Correct group reference
            .replace("{\\1}", r"\1")  # Correct group reference
            .replace("{\\2}", r"\2")  # Correct group reference
            .replace("{\\3}", r"\3")  # Correct group reference
            .replace("{\\w}", r"\w")  # Correct group reference
            .replace("{\\s}", r"\s")  # Correct group reference
        )
    return rules

def apply_rules(text, rules):
    """Applies rules to the given text."""
    for pattern in rules["padroes"]:
        text = re.sub(pattern["regex"], pattern["sub"], text)
    return text

if __name__ == "__main__":
    import tonic
    # Load the rules from the JSON file
    rules_file = "rules.json"  # Update the path to your JSON file
    rules = load_rules(rules_file)

    # Prepare the patterns with placeholders replaced
    rules = prepare_patterns(rules)

    # Input text to process
    input_text = " " + input("Digite o texto: ")

    # Apply the rules to the input text
    output_text = apply_rules(input_text, rules)

    # Display the result
    print("Texto original:", input_text)
    print("Texto processado:", output_text)
    separated = output_text.split("@")
    tonicNumber = tonic.tonic(separated)
    print("Sílaba tônica:", tonicNumber)
