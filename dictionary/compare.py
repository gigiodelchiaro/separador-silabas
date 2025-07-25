import json
import subprocess
import os
import time
from typing import List, Optional, Tuple
from tqdm import tqdm
import concurrent.futures
import re

def run_syllabification(word: str) -> Optional[List[str]]:
    """
    Executes the syllable.py script for a given word and returns the syllabified word as a list of strings.
    """
    script_path = os.path.join(os.path.dirname(__file__), 'old', 'syllable.py')
    try:
        process = subprocess.run(
            ['python3', script_path, word],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return process.stdout.strip().split('-')
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # print(f"Error processing word '{word}' with syllable.py: {e}") # Suppress for cleaner output
        return None

def get_tonic_syllable_position(syllables: List[str]) -> Optional[int]:
    """
    Determines the position of the tonic syllable from the end of the word (1-based).
    """
    if not syllables:
        return None

    strong_accents = 'áéíóúàèìòùâêîôûÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ'
    weak_accents = 'ãẽĩõũÃẼĨÕŨ'

    for i, syllable in enumerate(reversed(syllables)):
        if any(char in strong_accents for char in syllable):
            return i + 1
    
    for i, syllable in enumerate(reversed(syllables)):
        if any(char in weak_accents for char in syllable):
            return i + 1

    last_syllable = syllables[-1]
    pattern = r'[iIuU]s?|[aA]is|[eE]is|[oO]is|[uU]ns|[eE]ns|[rRlLzZ]$'
    
    if re.search(pattern, last_syllable, re.IGNORECASE):
        return 1
    
    if len(syllables) > 1 and re.search(pattern, syllables[-2], re.IGNORECASE):
        return 2

    return 2

def process_word_entry(entry: dict) -> Tuple[bool, bool, Optional[str], bool, dict]:
    """
    Processes a single word entry from the dictionary, performing syllabification
    and tonic calculation, and returning correctness flags, warnings, and a validity flag.
    Returns: (syllabification_correct, tonic_correct, warning_message, is_valid_entry, entry_data)
    """
    word = entry.get("word")
    true_syllables = entry.get("syllables")
    true_tonic_position = entry.get("tonic")

    syllabification_correct = False
    tonic_correct = False
    warning_message = None
    is_valid_entry = True # Assume valid unless proven otherwise

    if not word or not true_syllables or true_tonic_position is None:
        warning_message = f"Skipping malformed entry: {entry}"
        is_valid_entry = False
        return syllabification_correct, tonic_correct, warning_message, is_valid_entry, entry

    predicted_syllables = run_syllabification(word)

    if predicted_syllables:
        if predicted_syllables == true_syllables:
            syllabification_correct = True
        else:
            warning_message = f"Syllabification mismatch for '{word}': Expected {true_syllables}, Got {predicted_syllables}"
    else:
        warning_message = f"Failed to syllabify '{word}'"

    # Only check tonic if syllabification was successful (predicted_syllables is not None)
    # and if the syllabification was correct (syllabification_correct is True)
    if predicted_syllables and syllabification_correct:
        predicted_tonic_position = get_tonic_syllable_position(predicted_syllables)
        
        if predicted_tonic_position is not None and predicted_tonic_position == true_tonic_position:
            tonic_correct = True
        else:
            if warning_message: # Append to existing warning if any
                warning_message += f"; Tonic mismatch for '{word}': Expected {true_tonic_position}, Got {predicted_tonic_position}"
            else:
                warning_message = f"Tonic mismatch for '{word}': Expected {true_tonic_position}, Got {predicted_tonic_position}"

    return syllabification_correct, tonic_correct, warning_message, is_valid_entry, entry

def compare_syllabification():
    """
    Compares the output of syllable.py with the expected syllables from a dictionary
    using multithreading, and generates a detailed report.
    """
    dictionary_path = os.path.join(os.path.dirname(__file__), 'filtered_dictionary.json')
    
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            dictionary_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading dictionary file: {e}")
        return

    correct_syllabification_count = 0
    correct_tonic_count = 0
    total_valid_words = 0
    all_warnings = []
    incorrect_words = []  # Store incorrect words for report

    start_time = time.time()

    # Use ThreadPoolExecutor for parallel processing
    num_workers = os.cpu_count() * 2 if os.cpu_count() else 4 # Default to 4 if cpu_count is None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        results_iterator = tqdm(executor.map(process_word_entry, dictionary_data),
                                total=len(dictionary_data),
                                desc="Processing words")
        
        for syllab_correct, tonic_correct, warning_msg, is_valid_entry, entry in results_iterator:
            if is_valid_entry:
                total_valid_words += 1
            
            if warning_msg:
                all_warnings.append(warning_msg)
                
                # Collect incorrect words for detailed report
                if not syllab_correct or not tonic_correct:
                    word = entry.get("word", "Unknown")
                    true_syllables = entry.get("syllables", [])
                    true_tonic = entry.get("tonic", "Unknown")
                    predicted_syllables = run_syllabification(word) if word != "Unknown" else None
                    predicted_tonic = get_tonic_syllable_position(predicted_syllables) if predicted_syllables else "Failed"
                    
                    incorrect_entry = {
                        "word": word,
                        "expected_syllables": true_syllables,
                        "predicted_syllables": predicted_syllables if predicted_syllables else "Failed",
                        "expected_tonic": true_tonic,
                        "predicted_tonic": predicted_tonic,
                        "error": warning_msg
                    }
                    incorrect_words.append(incorrect_entry)
            
            if syllab_correct:
                correct_syllabification_count += 1
            if tonic_correct:
                correct_tonic_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Generate report
    if total_valid_words > 0:
        syllabification_accuracy = (correct_syllabification_count / total_valid_words) * 100
        tonic_accuracy = (correct_tonic_count / total_valid_words) * 100
        
        print(f"\n--- Comparison Results ---")
        print(f"Total valid words processed: {total_valid_words}")
        print(f"Syllabification Accuracy: {syllabification_accuracy:.2f}% ({correct_syllabification_count}/{total_valid_words})")
        print(f"Tonic Syllable Accuracy: {tonic_accuracy:.2f}% ({correct_tonic_count}/{total_valid_words})")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")

        # Create detailed report
        report_content = f"""SYLLABIFICATION AND TONIC ANALYSIS REPORT
==============================

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total valid words processed: {total_valid_words}
Syllabification Accuracy: {syllabification_accuracy:.2f}% ({correct_syllabification_count}/{total_valid_words})
Tonic Syllable Accuracy: {tonic_accuracy:.2f}% ({correct_tonic_count}/{total_valid_words})
Processing Time: {elapsed_time:.2f} seconds

SUMMARY OF ERRORS
=================
Total warnings: {len(all_warnings)}

DETAILED ERROR ANALYSIS
======================="""

        for i, word_data in enumerate(incorrect_words, 1):
            report_content += f"""
{i}. Word: {word_data['word']}
   Expected Syllables: {'-'.join(word_data['expected_syllables']) if isinstance(word_data['expected_syllables'], list) else word_data['expected_syllables']}
   Predicted Syllables: {'-'.join(word_data['predicted_syllables']) if isinstance(word_data['predicted_syllables'], list) else word_data['predicted_syllables']}
   Expected Tonic Position: {word_data['expected_tonic']}
   Predicted Tonic Position: {word_data['predicted_tonic']}
   Error: {word_data['error']}
"""

        # Save report to file
        report_filename = f"syllabification_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        print(f"\nDetailed report saved to: {report_filename}")

        # Save incorrect words to separate file
        incorrect_words_filename = f"incorrect_words_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(incorrect_words_filename, 'w', encoding='utf-8') as incorrect_file:
            for word_data in incorrect_words:
                incorrect_file.write(f"{word_data['word']}\n")
        
        print(f"Incorrect words list saved to: {incorrect_words_filename}")

        # Show sample of warnings if there are any
        if all_warnings:
            print(f"\n--- Sample Warnings (showing first 10) ---")
            for warning in all_warnings[:10]:
                print(warning)
            if len(all_warnings) > 10:
                print(f"... and {len(all_warnings) - 10} more warnings.")
    else:
        print("No valid words were processed from the dictionary.")

if __name__ == "__main__":
    compare_syllabification()