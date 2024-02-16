import requests
from bs4 import BeautifulSoup
import os

def make_absolute_url(base, url):
    # Chuyển đổi một URL tương đối thành tuyệt đối
    from urllib.parse import urljoin
    return urljoin(base, url)

def download_file(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, url.split('/')[-1])
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {filename}')

def download_website_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all('link', {'rel': 'stylesheet'}):
        css_url = link.get('href')
        if css_url:
            absolute_css_url = make_absolute_url(url, css_url)
            download_file(absolute_css_url, 'css')

    for script in soup.find_all('script'):
        js_url = script.get('src')
        if js_url:
            absolute_js_url = make_absolute_url(url, js_url)
            download_file(absolute_js_url, 'js')

    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            absolute_img_url = make_absolute_url(url, img_url)
            download_file(absolute_img_url, 'images')

if __name__ == '__main__':
    website_url = 'https://websmirno.site/medin/html/medlab-html/index.html'
    download_website_content(website_url)
