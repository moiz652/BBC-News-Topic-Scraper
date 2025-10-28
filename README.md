# BBC News Topic Scraper

This Python script uses Playwright to scrape the BBC News website for articles related to a user-provided topic. It then scrapes the full text of each relevant article, generates a 3-sentence summary using `sumy`, and saves the results to a clean `.txt` file.

This project demonstrates skills in:
* Browser automation with **Playwright**
* Finding and updating fragile **CSS selectors**
* Debugging dynamic (JavaScript-loaded) websites
* Handling strict-mode violations
* Extractive text summarization with **sumy**
* Saving structured data to a file

## 🚀 Features

* **Topic Search:** Prompts the user for any search topic.
* **Smart Filtering:** Uses a 2-pass system. It filters results on the search page (by title and snippet) *before* visiting the links to ensure high relevance.
* **Article Summarization:** Scrapes the full text of each article and generates a concise summary.
* **File Output:** Saves the headline, link, and summary for each article to a dynamically named `.txt` file (e.g., `bitcoin_news.txt`).

## 🛠️ How to Use

### 1. Setup

First, clone this repository:
```bash
git clone [https://github.com/YOUR-USERNAME/BBC-News-Topic-Scraper.git](https://github.com/YOUR-USERNAME/BBC-News-Topic-Scraper.git)
cd BBC-News-Topic-Scraper
```

Next, install the required Python libraries:
```bash
pip install -r requirements.txt
```

Finally, you must run the one-time setup commands for Playwright (to install browsers) and NLTK (to download language data for summarization):
```bash
python -m playwright install
python -m nltk.downloader punkt
```

### 2. Run the Script

Once setup is complete, simply run the script:
```bash
python scrape_bbc_news.py
```

The script will ask you for a topic and then begin scraping, saving the results in the same directory.

## 📄 Example Output (`bitcoin_news.txt`)

```
News articles found for: bitcoin
Source URL: [https://www.bbc.com/search?q=bitcoin](https://www.bbc.com/search?q=bitcoin)
=========================================

Headline: Bitcoin worth $14bn seized in US-UK crackdown on alleged scammers
Link: [https://www.bbc.com/news/articles/c70jw436n0yo](https://www.bbc.com/news/articles/c70jw436n0yo)
Summary:
* The US government has seized more than $14bn (£10.5bn) in bitcoin...
* Mr Chen, who remains at large, is accused of being the mastermind behind...
* Cooper said: "Together with our US allies, we are taking decisive action..."
-----------------------------------------

Headline: Chinese woman convicted after 'world's biggest' bitcoin seizure
Link: [https://www.bbc.com/news/articles/cy0415kk3rzo](https://www.bbc.com/news/articles/cy0415kk3rzo)
Summary:
* On Tuesday, the Court heard that confiscation proceedings had begun...
* Wen, 44, laundered the proceeds from the scam and moved from living...
* Monday's conviction marks the "culmination of years of dedicated investigation"...
-----------------------------------------
```
