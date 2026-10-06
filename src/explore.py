import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EIA_API_KEY")
print("Kalit topildimi:", api_key is not None)

url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[0]": "value",
    "facets[series][]": "RWTC",
    "start": "2026-09-01",
}
response = requests.get(url, params=params)
print("Status kodi:", response.status_code)
data = response.json()
print("Yuqori kalitlar:", list(data.keys()))
data = response.json()
print("Jami qatorlar:", data["response"]["total"])
print("Kalit javob ichida bormi:", api_key in response.text)