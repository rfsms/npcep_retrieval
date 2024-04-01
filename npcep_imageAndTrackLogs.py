from bs4 import BeautifulSoup
import requests
import os
import json

config_file_path = r"C:\NOAA_Scripts\urls.json"
with open(config_file_path, 'r', encoding='utf=8') as json_file:
    config_data = json.load(json_file)

print(config_data)

image_urls = config_data['image_urls']
tracklog_urls = config_data['tracklog_urls']
allowed_folders = config_data['allowed_folders']

def download_file(file_url, file_path, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(file_url)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {file_path}")
            break
        except Exception as e:
            print(f"Failed to download {file_url}. Retry {retries + 1}/{max_retries}. Error: {e}")
            retries += 1

# Images first
for folder_name, base_url in image_urls.items():
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a')
    folder_path = f"C:/NOAA_Scripts/images/{folder_name}/"
    os.makedirs(folder_path, exist_ok=True)

    for link in links:
        href = link.get('href')
        if "band4" in href and href.endswith('.jpg') and not href.endswith('.thumb.jpg'):
            file_path = os.path.join(folder_path, href)
            if not os.path.exists(file_path):
                file_url = base_url + href
                download_file(file_url, file_path)
            else:
                print(f"File {href} already exists. Skipping download.")

# Now lets do tracklogs
for folder_name, base_url in tracklog_urls.items():
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a')
    folder_path = f"C:/NOAA_Scripts/images/track_logs/{folder_name}/"
    os.makedirs(folder_path, exist_ok=True)

    links = [link for link in soup.find_all('a') if any (allowed in link.get('href') for allowed in allowed_folders)]

    for link in links:
        subfolder_name = link.get('href').strip('/')
        subfolder_url = base_url + subfolder_name
        subfolder_path = os.path.join(f"c:/NOAA_Scripts/images/track_logs/{folder_name}/", subfolder_name)
        
        #Ensure directory exists
        os.makedirs(subfolder_path, exist_ok=True)

        #Fetch the content
        subfolder_response = requests.get(subfolder_url)
        subfolder_soup = BeautifulSoup(subfolder_response.text, 'html.parser')

        for file_link in subfolder_soup.find_all('a'):
            file_href = file_link.get('href')
            if file_href.endswith('.csv') or file_href.endswith('.png'):
                file_url = subfolder_url + '/' + file_href
                file_path = os.path.join(subfolder_path, file_href)
                if not os.path.exists(file_path):
                    download_file(file_url, file_path)
