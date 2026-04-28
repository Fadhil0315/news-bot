import feedparser

url = "https://news.google.com/rss/search?q=geopolitics+OR+war+OR+conflict&hl=en-IN&gl=IN&ceid=IN:en"

feed = feedparser.parse(url)

for i, entry in enumerate(feed.entries[:10], start=1):
    print(f"{i}. {entry.title}")