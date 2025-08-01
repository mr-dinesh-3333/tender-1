import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from urllib.parse import urljoin


def scrape_eprocure():
    base_url = 'https://eprocure.gov.in'
    url = 'https://eprocure.gov.in/cppp/latestactivetendersnew/cpppdata'
    tenders = []

    try:
        # Use cookies to bypass access restrictions
        cookies = {'cookieWorked': 'yes'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for page in range(1, 6):  # Scrape first 5 pages
            params = {'page': page}
            response = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'table'})

            if not table:
                break

            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue

                try:
                    title_cell = cells[4].find('a')
                    title = title_cell.text.strip()
                    relative_url = title_cell['href']
                    full_url = urljoin(base_url, relative_url)

                    tender = {
                        "source": "eProcure",
                        "tender_id": cells[4].text.strip()[:100],
                        "title": title,
                        "publish_date": cells[1].text.strip(),
                        "closing_date": cells[2].text.strip(),
                        "organisation": cells[5].text.strip(),
                        "url": full_url,
                        "scraped_at": datetime.now()
                    }

                    tenders.append(tender)
                except Exception as e:
                    logging.error(f"Error parsing eProcure tender: {e}")

    except Exception as e:
        logging.error(f"Error scraping eProcure: {e}")

    return tenders