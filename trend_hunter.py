from pytrends.request import TrendReq

def get_daily_trends():
    """Fetches the top daily search trends in the US to feed the Image Agent."""
    print("Waking up Trend Sniper...")
    
    # Initialize connection to Google Trends
    pytrend = TrendReq(hl='en-US', tz=360)
    
    print("Hunting current trends...")
    try:
        # Fetch trending searches for today
        trending_today = pytrend.trending_searches(pn='united_states')
        
        # Clean up the data into a simple list
        top_trends = trending_today[0].tolist()
        
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
