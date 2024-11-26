import requests

def fetch_proxies():
    """Fetches proxies from the API and saves them to 'auto_proxies.txt'."""
    api_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    try:
        response = requests.get(api_url, stream=True)
        if response.status_code == 200:
            proxies = response.text.strip().splitlines()
            if proxies:
                with open('auto_proxies.txt', 'w') as f:
                    f.writelines([proxy + '\n' for proxy in proxies])
                print(f"Fetched and saved {len(proxies)} proxies to 'auto_proxies.txt'.")
            else:
                print("No proxies found from the API.")
                return False
        else:
            print(f"Failed to fetch proxies. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return False
    return True


fetch_proxies()