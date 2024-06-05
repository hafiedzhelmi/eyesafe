import requests
import os
import time

# Function to create a directory for the dataset
def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to download images and check for duplicates
def download_images(images, save_folder, total_images, num_images):
    create_dir(save_folder)
    existing_files = set(os.listdir(save_folder))  # Get a list of already downloaded files to avoid duplication
    for img in images:
        img_url = img["link"]
        img_name = img_url.split('/')[-1]  # Using the last part of the URL as the file name
        if img_name in existing_files:
            print(f"Skipping {img_name} as it already exists.")
            continue
        try:
            img_data = requests.get(img_url, timeout=10).content
            with open(os.path.join(save_folder, img_name), 'wb') as handler:
                handler.write(img_data)
            print(f"Downloaded {img_name} to {save_folder}")
            total_images += 1  # Increment only on successful download
            if total_images >= num_images:  # Check if the required number of images has been downloaded
                return total_images
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")
    return total_images

# Function to search images using Google Custom Search JSON API
def search_images(query, api_key, cse_id, save_folder, num_images=50):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': cse_id,
        'key': api_key,
        'searchType': 'image',
        'num': 10  # Maximum number of images per request
    }
    
    total_images = 0
    while total_images < num_images:
        response = requests.get(url, params=params).json()
        images = response.get('items', [])
        if not images:
            break
        total_images = download_images(images, save_folder, total_images, num_images)
        if total_images >= num_images:
            break
        time.sleep(1)  # Respect Google's rate limit

        if 'nextPage' in response['queries']:
            params['start'] = response['queries']['nextPage'][0]['startIndex']
        else:
            break

# Main code
API_KEY = 'AIzaSyBdbanHZyXzf_8qy5tDm1f_A8so5BQRpSs'
CSE_ID = '4097f06a0126047d8'

search_images('men smart casual', API_KEY, CSE_ID, 'D:\\google\\level5man', num_images=300)
search_images('full dressed woman', API_KEY, CSE_ID, 'D:\\google\\level5woman', num_images=300)
