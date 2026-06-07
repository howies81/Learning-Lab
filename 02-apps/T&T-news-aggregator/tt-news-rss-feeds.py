import feedparser
import socket
import pandas as pd
from datetime import datetime
import os


application_path = os.getcwd()
year_month_day = datetime.today().strftime("%Y-%m-%d")


queries = {
    
    #"Trinidad_Guardian": 'https://rssgenerator.mooo.com/feeds/?p=aaHR0cHM6Ly9ndWFyZGlhbi5jby50dC8=',
    "CNC3 Television": 'https://www.cnc3.co.tt/feed/',
    "TTT Live Online": 'https://www.ttt.live/feed/',
    "Trinidad Express (via Google)": 'https://news.google.com/rss/search?q=site:trinidadexpress.com',
    "Wired 868": 'https://news.google.com/rss/search?q=site:wired868.com'
}

socket.setdefaulttimeout(20)
Trinidad_news = []
for source, url in queries.items():
    print(f"\n ===Printing: {source}===")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"Skipping source in {source} due to connection timeout: {e}")

    for entry in feed.entries[:20]:
        all_articles = {
            "news_source": source,
            "news_title": entry.title,
            "news_link": entry.link,
            "news_publish_date": entry.published
        }
        Trinidad_news.append(all_articles)

news_df = pd.DataFrame(Trinidad_news)

print(news_df)
# Create a dedicated 'data' folder if it doesn't exist yet
data_folder = os.path.join(application_path, "data")
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Update your final file path to save inside that folder
file_name = f"trinidad_news_{year_month_day}.csv"
final_path = os.path.join(data_folder, file_name)

# Try to save the CSV file
try:
    # Now save cleanly inside /data/
    news_df.to_csv(final_path, index=None)
    print(f"✓ Successfully saved to trinidad_news_{year_month_day}.csv")
except Exception as e:
    print(f"❌ Error saving CSV file: {e}")