import time
import re
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

# --- Sumy (Summarizer) Imports ---
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# --- Configuration ---
# Selectors found for BBC News (as of Oct 2025)
SEARCH_RESULT_SELECTOR = 'a:has(div[data-testid="newport-article"])'
TITLE_LINK_SELECTOR = 'h2[data-testid="card-headline"]'
SNIPPET_SELECTOR = 'div.sc-cdecfb63-3'
TEXT_SELECTOR = 'article p'
SEARCH_INPUT_SELECTOR = 'input[data-testid="search-input-field"]:not([disabled])' 

MAX_ARTICLES_TO_SAVE = 5
SENTENCES_COUNT = 3

# --- Setup for Summarizer ---
LANGUAGE = "english"
stemmer = Stemmer(LANGUAGE)
stop_words = get_stop_words(LANGUAGE)
summarizer = Summarizer(stemmer)
summarizer.stop_words = stop_words

# --- STEP 1: Get user input ---
USER_TOPIC = input("What topic do you want to search for? ")
if not USER_TOPIC:
    print("No topic entered. Exiting.")
    exit()

# --- STEP 2: Create the search URL and output filename ---
SEARCH_URL = f"https://www.bbc.com/search?q={USER_TOPIC.lower()}"
safe_filename = re.sub(r'[^a-zA-Z0-9_]', '', USER_TOPIC.lower().replace(' ', '_'))
OUTPUT_FILENAME = f"{safe_filename}_news.txt"
found_articles_count = 0

print(f"Searching for '{USER_TOPIC}'... Results will be saved to {OUTPUT_FILENAME}")

# Clear the file to start fresh
with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
    f.write(f"News articles found for: {USER_TOPIC}\n")
    f.write(f"Source URL: {SEARCH_URL}\n")
    f.write("=========================================\n\n")

print("Starting browser...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # --- STEP 3: Go to the search results page ---
    print(f"Going to {SEARCH_URL}...")
    page.goto(SEARCH_URL, wait_until="domcontentloaded")
    
    # Get the corrected search term from the page
    corrected_topic = page.locator(SEARCH_INPUT_SELECTOR).get_attribute('value')
    print(f"Search term on page: '{corrected_topic}'")
    
    print("Finding all search results on the page...")
    search_results = page.locator(SEARCH_RESULT_SELECTOR).all()

    if not search_results:
        print("No search results found on the page. Exiting.")
        browser.close()
        exit()

    print(f"Found {len(search_results)} search results. Now filtering...")

    articles_to_scrape = []
    
    # --- STEP 4: First Pass - Filter on Search Page ---
    for result in search_results:
        try:
            title_element = result.locator(TITLE_LINK_SELECTOR)
            snippet_element = result.locator(SNIPPET_SELECTOR)

            title = title_element.text_content().strip()
            href = result.get_attribute('href') 
            snippet = snippet_element.text_content().strip()

            if not title or not href:
                continue

            # Filter by original AND corrected topic
            user_topic_low = USER_TOPIC.lower()
            corrected_topic_low = corrected_topic.lower()
            
            if (user_topic_low in title.lower() or 
                corrected_topic_low in title.lower() or 
                user_topic_low in snippet.lower() or 
                corrected_topic_low in snippet.lower()):
                
                print(f"-> RELEVANT: {title}")
                full_url = urljoin(SEARCH_URL, href)
                if not any(a['url'] == full_url for a in articles_to_scrape):
                    articles_to_scrape.append({'url': full_url, 'title': title})
            
        except Exception as e:
            print(f"Skipping a non-article item: {e}")
            
    if not articles_to_scrape:
        print(f"No results on this page matched '{USER_TOPIC}' or '{corrected_topic}' in their title or snippet.")
        browser.close()
        exit()

    # --- STEP 5: Second Pass - Scrape and Save Matches ---
    print(f"\nFound {len(articles_to_scrape)} relevant articles. Now scraping...")
    
    for i, article in enumerate(articles_to_scrape):
        if i >= MAX_ARTICLES_TO_SAVE:
            print(f"Saved first {MAX_ARTICLES_TO_SAVE} articles. Stopping.")
            break
        
        url = article['url']
        title = article['title']
        print(f"\nScraping Article {i+1}: {title}...")
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            text_elements = page.locator(TEXT_SELECTOR).all_text_contents()
            
            if not text_elements:
                print("-> Could not find article text. Skipping.")
                continue

            full_text = " ".join(text_elements)
            found_articles_count += 1
            
            print("-> Summarizing...")
            parser = PlaintextParser.from_string(full_text, Tokenizer(LANGUAGE))
            summary_sentences = summarizer(parser.document, SENTENCES_COUNT)
            summary_text = "\n".join([f"* {sentence}" for sentence in summary_sentences])

            print(f"-> Saving to {OUTPUT_FILENAME}...")
            with open(OUTPUT_FILENAME, 'a', encoding='utf-8') as f:
                f.write(f"Headline: {title}\n")
                f.write(f"Link: {url}\n")
                f.write(f"Summary:\n{summary_text}\n")
                f.write("-----------------------------------------\n\n")
        
        except Exception as e:
            print(f"-> Could not scrape {url}. Error: {e}")
        
        time.sleep(1)

    browser.close()
    
    print("\n=========================================")
    print("Done.")
    print(f"Saved {found_articles_count} relevant articles.")
    print(f"Check {OUTPUT_FILENAME} for the results.")
