import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_images(url, folder_path, visited_urls=None, downloaded_images=None):
    if visited_urls is None:
        visited_urls = set()

    if downloaded_images is None:
        downloaded_images = set()

    if url in visited_urls:
        return
    visited_urls.add(url)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    img_tags = soup.findAll('img')
    a_tags = soup.findAll('a')

    urls_to_visit = set()

    for a in a_tags:
        href = a.attrs.get("href")
        if href and urlparse(href).scheme:
            full_url = urljoin(url, href)
            if not full_url in visited_urls:
                urls_to_visit.add(full_url)
        elif href:
            full_url = urljoin(url, href)
            if not full_url in visited_urls:
                urls_to_visit.add(full_url)

    for img in img_tags:
        img_url = img.attrs.get("src") or img.attrs.get("data-src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        filename = os.path.join(folder_path, img_url.split("/")[-1].split("?")[0])

        if filename in downloaded_images:
            print(f"Hình ảnh đã tồn tại, bỏ qua: {filename}")
            continue

        with requests.get(img_url, stream=True) as r:
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_images.add(filename)
                print(f"Hình ảnh đã được tải xuống: {filename}")
            else:
                print(f"Không thể tải hình ảnh: {img_url}")

    for next_url in urls_to_visit:
        new_folder_path = os.path.join(folder_path, urlparse(next_url).path.strip("/").replace("/", "_"))
        download_images(next_url, new_folder_path, visited_urls, downloaded_images)

# Ví dụ sử dụng
url = 'https://themetechmount.com/html/labostica/index.html'
folder_path = 'downloaded_images'
download_images(url, folder_path)