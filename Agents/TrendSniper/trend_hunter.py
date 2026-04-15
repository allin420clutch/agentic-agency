import requests
import xml.etree.ElementTree as ET

def get_daily_trends():
    """Fetches the top daily search trends by bypassing the broken API and reading Google's raw XML feed."""
    print("Waking up Trend Sniper...")
    print("Hunting current trends directly from Google's data feed...")
    
    # Google's official, unblockable RSS feed for daily trends
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    
    try:
        # Fetch the raw XML data
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the XML
        root = ET.fromstring(response.content)
        
        top_trends = []
        # Find all the trending topics in the feed
        for item in root.findall('.//item'):
            title = item.find('title').text
            if title:
                top_trends.append(title)
                
        print("\n--- TOP 5 TRENDS RIGHT NOW ---")
        for i, trend in enumerate(top_trends[:5], 1):
            print(f"{i}. {trend}")
            
        return top_trends[:5]
        
    except Exception as e:
        print(f"Error hunting trends: {e}")
        return []

if __name__ == "__main__":
    # Test the agent's eyes
    trends = get_daily_trends()
