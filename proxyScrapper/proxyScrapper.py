import requests

# Step 1: Download the file from a GitHub repository (or any URL)
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/US/data.txt"  # Replace with the actual GitHub URL
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    # Step 2: Read the content
    proxies_text = response.text.splitlines()  # Split into lines

    # Step 3: Split the proxies into chunks of 1000 lines
    chunk_size = 1000
    num_chunks = len(proxies_text) // chunk_size + (1 if len(proxies_text) % chunk_size != 0 else 0)

    # Step 4: Write each chunk to a separate file
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = proxies_text[start:end]

        # Create a new file for each chunk
        with open(f"proxies_part_{i + 1}.txt", "w") as f:
            f.write("\n".join(chunk))

    print(f"File split into {num_chunks} parts.")

else:
    print("Failed to download the file. HTTP status code:", response.status_code)
