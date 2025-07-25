import requests
import os
import time
import logging
from bs4 import BeautifulSoup

# --- Configuration ---
BASE_URL = "http://www.portaldalinguaportuguesa.org/index.php"
OUTPUT_DIR = "html"  # A main directory to store all letter folders

# Configure logging for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_pages_for_letter(letter):
    """
    Downloads all HTML pages for a given starting letter, handling pagination.

    Args:
        letter (str): The letter to download pages for.
    """
    start_param = 0
    page_count = 0

    # Create a directory for the letter
    letter_dir = os.path.join(OUTPUT_DIR, letter)
    os.makedirs(letter_dir, exist_ok=True)

    logger.info(f"Starting to download pages for letter: {letter}")

    while True:
        params = {
            'action': 'syllables',
            'act': 'list',
            'letter': letter,
            'start': start_param
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch page for letter '{letter}' with start={start_param}: {e}")
            break  # Stop for this letter on network error

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check if the page has content before saving
        target_table = soup.find('table', id='rollovertable')
        if not target_table or len(target_table.find_all('tr')) <= 1:
            logger.info(f"No data rows found on page for letter '{letter}', start={start_param}. This is the end of pagination.")
            break

        # Save the HTML content
        file_path = os.path.join(letter_dir, f"start_{start_param}.html")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"Saved page to {file_path}")
        except IOError as e:
            logger.error(f"Failed to write HTML to {file_path}: {e}")

        page_count += 1

        # --- Pagination Logic ---
        # Find the 'seguintes' (next) link
        next_link_found = soup.find('a', string='seguintes')

        if next_link_found:
            start_param += 100  # The site uses 100 items per page
            time.sleep(0.1)  # Be respectful to the server
        else:
            logger.info(f"Reached the end of pagination for letter '{letter}' after {page_count} pages.")
            break

    logger.info(f"Finished downloading pages for letter '{letter}'. Total pages downloaded: {page_count}")


def main():
    """
    Main function to orchestrate the downloading process for all letters.
    """
    # Create the main output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]

    logger.info("Starting the page downloading process for all letters.")

    for letter in alphabet:
        download_pages_for_letter(letter)

    logger.info("Downloading complete.")


if __name__ == "__main__":
    main()