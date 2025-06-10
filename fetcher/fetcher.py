import requests
import time

class DexscreenerFetcher:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_new_tokens(self):
        try:
            r = requests.get(self.api_url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                tokens = []
                if isinstance(data, list):
                    for token in data:
                        token["fetched_at"] = time.time()
                        tokens.append(token)
                return tokens
            else:
                return []
        except Exception as e:
            print(f"Fetch error: {e}")
            return []