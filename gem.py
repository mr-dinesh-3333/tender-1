import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime


def scrape_gem():
    url = 'https://gem.gov.in/all-tenders'
    tenders = []

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'table'})

        if not table:
            return tenders

        for row in table.find_all('tr')[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) < 8:
                continue

            try:
                title_cell = cells[1].find('a')
                title = title_cell.text.strip()
                tender_url = title_cell['href']

                tender = {
                    "source": "GEM",
                    "tender_id": cells[0].text.strip(),
                    "title": title,
                    "publish_date": cells[2].text.strip(),
                    "closing_date": cells[3].text.strip(),
                    "organisation": cells[4].text.strip(),
                    "url": tender_url,
                    "scraped_at": datetime.now()
                }

                tenders.append(tender)
            except Exception as e:
                logging.error(f"Error parsing GEM tender: {e}")

    except Exception as e:
        logging.error(f"Error scraping GEM: {e}")

    return tenders