import praw
import requests
import cv2
import numpy as np
import os
import pickle
from urllib.parse import urlparse
import time
import urllib3
from requests.adapters import HTTPAdapter

from utils.create_token import create_token

def requests_retry_session(retries=5, backoff_factor=1, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = urllib3.util.retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def create_folder(image_path):
    if not os.path.isdir(image_path):
        os.makedirs(image_path)

def select_file_from_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for i, file in enumerate(files, 1):
        print(f"{i}: {file}")
    choice = int(input("Enter the number to select a text file: ")) - 1
    return files[choice]

dir_path = os.path.dirname(os.path.realpath(__file__))
image_path = "D:\\scraped images\\"
source_url_path = r"C:\nsfw_data_source_urls-master\nsfw_data_source_urls-master\source_urls"

selected_file = select_file_from_folder(source_url_path)
selected_file_path = os.path.join(source_url_path, selected_file)
subreddit_folder = os.path.join(image_path, selected_file.replace('.txt', ''))
create_folder(subreddit_folder)

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    creds = create_token()
    with open("token.pickle", "wb") as pickle_out:
        pickle.dump(creds, pickle_out)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     username=creds.get('username', ''),
                     password=creds.get('password', ''))

POST_SEARCH_AMOUNT = 300
RATE_LIMIT_SLEEP = 1.2

with open(selected_file_path, "r") as f_final:
    links_to_process = False
    for line in f_final:
        if 'links that work:' in line:
            links_to_process = True
            continue
        if not links_to_process:
            continue
        subreddit_url = line.strip()
        parsed_url = urlparse(subreddit_url)
        subreddit_name = parsed_url.path.split('/')[2]
        subreddit = reddit.subreddit(subreddit_name)

        print(f"Starting {subreddit_name}!")
        for submission in subreddit.new(limit=POST_SEARCH_AMOUNT):
            if "jpg" in submission.url.lower() or "png" in submission.url.lower() or "jpeg" in submission.url.lower():
                image_filename = f"{subreddit_name}-{submission.id}.png"
                image_filepath = os.path.join(subreddit_folder, image_filename)
                if os.path.exists(image_filepath):
                    print(f"Image already exists: {image_filename}")
                    continue

                try:
                    response = requests_retry_session().get(submission.url.lower(), stream=True, timeout=6).raw
                    image = np.asarray(bytearray(response.read()), dtype="uint8")
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                    compare_image = cv2.resize(image, (224, 224))
                    cv2.imwrite(image_filepath, compare_image)
                    print(f"Saved image {image_filename} from {subreddit_name}")

                    time.sleep(RATE_LIMIT_SLEEP)
                except requests.exceptions.Timeout:
                    print(f"Timeout occurred for URL: {submission.url.lower()}")
                except requests.exceptions.ConnectionError:
                    print(f"Connection error for URL: {submission.url.lower()}")
                except Exception as e:
                    print(f"Failed to download image from {submission.url.lower()}: {e}")
