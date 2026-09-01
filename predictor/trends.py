from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=330)

def get_google_trend(keyword):

    try:
        print("Searching Google Trends for:", keyword)

        pytrends.build_payload([keyword], timeframe='today 12-m')

        data = pytrends.interest_over_time()

        print(data)

        if data.empty:
            print("No Google Trends data found.")
            return 20

        score = int(data[keyword].mean())

        print("Google Trend Score:", score)

        return score

    except Exception as e:
        print("Google Trends Error:", e)
        return 50