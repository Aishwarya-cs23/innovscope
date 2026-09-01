from pytrends.request import TrendReq

pytrends = TrendReq()

keyword = ["Artificial Intelligence"]

pytrends.build_payload(
    keyword,
    timeframe='today 12-m'
)

data = pytrends.interest_over_time()

print(data.tail())