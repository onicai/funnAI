import requests
import math
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Define the collections to process
collections = [
    {"name": "icpp-art", "total_items": 2024},
    {"name": "charles", "total_items": 990},
]

base_url = "https://api.bioniq.io/v2/inscriptions"
common_params = {
    "search": "",
    "sort": "mint_number_desc",  # other options: "price_asc", "price_desc", "mint_number_asc"
    "protocol": "ckBTC"
}

for coll in collections:
    collection_name = coll["name"]
    total_items = coll["total_items"]
    params = common_params.copy()
    params.update({
        "collection": collection_name,
        "limit": total_items  # Assuming all items can be fetched in one call
    })

    num_pages = math.ceil(total_items / params["limit"])
    print(f"\nFetching data for collection '{collection_name}' from {num_pages} page(s)...")

    all_items_data = []

    for page_num in range(1, num_pages + 1):
        params["page"] = page_num
        print(f"Fetching page {page_num} for collection '{collection_name}'...")

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes

            data = response.json()
            items_key = 'results'

            if items_key in data and isinstance(data[items_key], list):
                items_on_page = data[items_key]
                all_items_data.extend(items_on_page)
                print(f"Successfully fetched {len(items_on_page)} items from page {page_num}")
            else:
                print(f"Warning: Could not find the expected items key '{items_key}' or its value is not a list on page {page_num}.")
                print(f"Response keys: {data.keys()}")
                break  # Stop if the expected data is not available

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_num} for collection '{collection_name}': {e}")
            break  # Stop on error

    print(f"Finished fetching for collection '{collection_name}'. Total items collected: {len(all_items_data)}")

    # Store the collected data in a dictionary
    data_dictionary = {"items": all_items_data}

    # Display summary for the collection
    if all_items_data:
        print(f"Data for collection '{collection_name}' stored in dictionary successfully.")
        # # Print first 5 items, if available
        # for idx, item in enumerate(all_items_data[:5], 1):
        #     print(f"Item {idx}: {item}")
        print(f"Total number of items stored: {len(all_items_data)}")
    else:
        print(f"No data collected for collection '{collection_name}'.")

    # Write the dictionary to a JSON file named <collection_name>.json
    EST = timezone(timedelta(hours=-5))
    timestamp = datetime.now(EST).strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = Path(__file__).parent / "snapshots" / f"{timestamp}_{collection_name.replace('-', '_')}.json"
    try:
        with open(output_filename, "w") as outfile:
            json.dump(data_dictionary, outfile, indent=4)
        print(f"Data for collection '{collection_name}' written to {output_filename}\n")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")
