import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import random

def make_absolute_url(base, url):
    return urljoin(base, url)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)

def download_file(url, base_folder):
    parsed_url = urlparse(url)
    # Tạo đường dẫn tệp dựa trên đường dẫn URL để giữ cấu trúc thư mục
    save_path = os.path.join(base_folder, parsed_url.path.lstrip('/'))
    directory = os.path.dirname(save_path)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f'Downloaded {url} to {save_path}')
        else:
            print(f'Failed to download {url}. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error downloading {url}. Error: {e}')

def download_fonts_from_css(content, base_url, base_folder):
    font_urls = re.findall(r'url\(([^)]+)\)', content)
    for font_url in font_urls:
        if not font_url.startswith('http'):
            font_url = make_absolute_url(base_url, font_url.strip('"\''))
        download_file(font_url, base_folder)

def save_html_content(content, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f'Saved HTML content to {path}')

def download_website_content(url):
    base_folder = 'downloaded_website'
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            save_html_content(html_content, os.path.join(base_folder, 'index.html'))

            # Download stylesheets
            for link in soup.find_all('link', {'rel': 'stylesheet'}):
                css_url = link.get('href')
                if css_url and "fonts.googleapis.com" not in css_url:
                    absolute_css_url = make_absolute_url(url, css_url)
                    download_file(absolute_css_url, base_folder)

            # Download JavaScript files
            for script in soup.find_all('script'):
                js_url = script.get('src')
                if js_url:
                    absolute_js_url = make_absolute_url(url, js_url)
                    download_file(absolute_js_url, base_folder)

            # Download images
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if img_url:
                    absolute_img_url = make_absolute_url(url, img_url)
                    download_file(absolute_img_url, base_folder)

            # NEW: Download images from data-background attributes
            for element in soup.find_all(True, {'data-background': True}):
                bg_url = element['data-background']
                if bg_url:
                    absolute_bg_url = make_absolute_url(url, bg_url)
                    download_file(absolute_bg_url, base_folder)
        else:
            print(f'Failed to load website {url}. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error loading website {url}. Error: {e}')


if __name__ == '__main__':
    website_url = 'https://topwebs.websitelayout.net/'
    download_website_content(website_url)
