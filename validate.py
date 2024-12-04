import requests
from requests.exceptions import RequestException
import time
import socks
import socket
from urllib.parse import urlparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_proxy(proxy_url, index, total):
    """
    Test if a proxy is alive, measure its latency, and handle HTTP, SOCKS4, SOCKS5 proxies with or without credentials.

    Args:
        proxy_url (str): Proxy in the format 'protocol://[user:pass@]ip:port'.
        index (int): Current proxy index in the list.
        total (int): Total number of proxies.

    Returns:
        dict: Proxy details with status, latency, and country.
    """
    parsed = urlparse(proxy_url)
    proxy_type = parsed.scheme.lower()
    host = parsed.hostname
    port = parsed.port
    username = parsed.username
    password = parsed.password

    result = {
        "proxy": proxy_url,
        "status": "Dead",
        "latency": None,
        "country": "Unknown",
    }

    try:
        if proxy_type in ["http", "https"]:
            proxy_dict = {
                "http": proxy_url,
                "https": proxy_url,
            }
            start_time = time.time()
            response = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
            latency = round((time.time() - start_time) * 1000, 2)

        elif proxy_type in ["socks4", "socks5"]:
            proxy_type_mapping = {"socks4": socks.SOCKS4, "socks5": socks.SOCKS5}
            socks.set_default_proxy(
                proxy_type_mapping[proxy_type],
                host,
                port,
                username=username,
                password=password,
            )
            socket.socket = socks.socksocket

            start_time = time.time()
            response = requests.get("http://httpbin.org/ip", timeout=5)
            latency = round((time.time() - start_time) * 1000, 2)

        else:
            return result

        if response.status_code == 200:
            result["status"] = "Alive"
            result["latency"] = latency
            result["country"] = get_proxy_country(host)

    except RequestException:
        pass

    print(f"[{index}/{total}] Processed proxy: {proxy_url}, Status: {result['status']}, Latency: {result['latency']} ms, Country: {result['country']}")
    return result


def get_proxy_country(ip):
    """
    Get the country of a proxy using the IP.

    Args:
        ip (str): IP address of the proxy.

    Returns:
        str: Country of the proxy or 'Unknown' if not found.
    """
    try:
        response = requests.get(f"http://ipinfo.io/{ip}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("country", "Unknown")
    except RequestException:
        pass
    return "Unknown"


def load_proxies(file_path):
    """
    Load proxies from a text file.

    Args:
        file_path (str): Path to the file containing proxies.

    Returns:
        list: List of proxy URLs.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]


def save_results_to_file(results, output_file):
    """
    Save proxy test results to a JSON file.

    Args:
        results (list): List of results with proxy details, latency, and country.
        output_file (str): Path to the output JSON file.
    """
    with open(output_file, "w") as file:
        json.dump(results, file, indent=4)


def process_proxies_concurrently(proxies, max_threads=10):
    """
    Process proxies using multithreading.

    Args:
        proxies (list): List of proxy URLs.
        max_threads (int): Number of threads to use.

    Returns:
        list: Results of proxy testing.
    """
    total = len(proxies)
    results = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {
            executor.submit(test_proxy, proxy, index + 1, total): proxy
            for index, proxy in enumerate(proxies)
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error processing proxy: {futures[future]} - {e}")
    return results


if __name__ == "__main__":
    file_path = "data.txt"  # Replace with the path to your file
    output_file = "proxy_results.json"  # File to save the results

    proxies = load_proxies(file_path)
    print(f"Loaded {len(proxies)} proxies from {file_path}.\n")

    # Test proxies concurrently
    results = process_proxies_concurrently(proxies, max_threads=20)

    # Save results
    save_results_to_file(results, output_file)
    print(f"\nResults saved to {output_file}")
