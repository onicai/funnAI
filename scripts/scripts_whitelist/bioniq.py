import requests
import pandas as pd
import math

# Base URL and parameters
base_url = "https://api.bioniq.io/v2/inscriptions"
collection = "charles"
total_items = 990
params = {
    "collection": "charles",
    "search": "",
    # Removed "status": "listed"
    "sort": "mint_number_desc", # other options: "price_asc", "price_desc", "mint_number_asc"
    "limit": total_items,
    "protocol": "ckBTC"
}

# Calculate the number of pages needed
num_pages = 1 # Since we want to get all items, we will not paginate
if "limit" in params.keys():
    limit_per_page = params["limit"]
    num_pages = math.ceil(total_items / limit_per_page)

print(f"Fetching data from {num_pages} pages...")

all_items_data = []

for page_num in range(1, num_pages + 1):
    params["page"] = page_num
    print(f"Fetching page {page_num}...")

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        items_key = 'results' 

        if items_key in data and isinstance(data[items_key], list):
            items_on_page = data[items_key]
            all_items_data.extend(items_on_page)
            print(f"Successfully fetched {len(items_on_page)} items from page {page_num}")
        else:
            print(f"Warning: Could not find the expected items key '{items_key}' or the value was not a list on page {page_num}.")
            print(f"Response keys: {data.keys()}")
            # Depending on the API, you might want to break or handle this differently
            break # Stop if we can't find the items data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        # You might want to implement retry logic here in a production script
        break # Stop on error

print(f"Finished fetching. Total items collected: {len(all_items_data)}")

# Create a pandas DataFrame from the collected data
if all_items_data:
    df = pd.DataFrame(all_items_data)
    print("\nDataFrame created successfully.")
    print(df.head()) # Print the first 5 rows
    print(f"\nDataFrame shape: {df.shape}")
else:
    print("\nNo data collected to create a DataFrame.")

# Example of how you might save the DataFrame
# df.to_csv("charles_collection_data.csv", index=False)
# df.to_json("charles_collection_data.json", orient="records")