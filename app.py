import os
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from dotenv import load_dotenv
from scrapers.eprocure import scrape_eprocure
from scrapers.gem import scrape_gem
from utils.alerts import send_whatsapp_alert, send_email
from summarize import summarize_tender

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tender_scraper.log"),
        logging.StreamHandler()
    ]
)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["gov_tenders"]
collection = db["tenders"]

# Filter keywords
FILTER_KEYWORDS = ['software', 'web development', 'web dev', 'AI', 'data entry', 'artificial intelligence']


def scrape_and_notify():
    """Main scraping function that runs daily"""
    logging.info("Starting daily tender scraping...")

    # Scrape all sources
    all_tenders = []
    all_tenders.extend(scrape_eprocure())
    all_tenders.extend(scrape_gem())
    # Add state scrapers here

    new_tenders = 0
    for tender in all_tenders:
        # Check if tender exists
        if collection.find_one({"tender_id": tender["tender_id"]}):
            continue

        # Save to database
        collection.insert_one(tender)
        new_tenders += 1

        # Generate summary
        summary = summarize_tender(
            tender["title"],
            tender["organisation"],
            tender["publish_date"],
            tender["closing_date"],
            tender["url"],
            os.getenv("GROQ_API_KEY")
        )

        # Prepare alert message
        message = f"🚀 *New Tender Alert!*\n\n"
        message += f"*Title:* {tender['title']}\n"
        message += f"*Organization:* {tender['organisation']}\n"
        message += f"*Publish Date:* {tender['publish_date']}\n"
        message += f"*Closing Date:* {tender['closing_date']}\n"
        message += f"*URL:* {tender['url']}\n\n"
        message += f"*Summary:*\n{summary}"

        # Send alerts
        send_whatsapp_alert(message)
        send_email("New Tender Alert", message.replace('*', ''))

    logging.info(f"Scraping complete. Found {new_tenders} new tenders.")


# Configure scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_and_notify, trigger="cron", hour=9)  # Run daily at 9 AM
scheduler.start()


@app.route('/')
def home():
    return "🚀 Government IT Tenders Monitor is running!"


@app.route('/scrape-now')
def scrape_now():
    scrape_and_notify()
    return jsonify({"status": "success", "message": "Scraping initiated"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)