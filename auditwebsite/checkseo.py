import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import sys
import io

# Thiết lập mã hóa cho đầu vào và đầu ra
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Đảm bảo mã hóa UTF-8
        return response.text
    except requests.RequestException as e:
        print(f"Lỗi khi truy cập {url}: {e}")
        return None

def check_seo(url):
    results = {'url': url}
    page_content = fetch_page(url)
    if not page_content:
        return results, []

    soup = BeautifulSoup(page_content, 'html.parser')

    # Tiêu đề trang (Title)
    title = soup.find('title')
    if title:
        results['title'] = title.text
        results['title_length'] = len(title.text)
    else:
        results['title'] = "Thiếu"
        results['title_length'] = 0

    # Thẻ mô tả (Meta Description)
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        results['meta_description'] = meta_description['content']
        results['meta_description_length'] = len(meta_description['content'])
    else:
        results['meta_description'] = "Thiếu"
        results['meta_description_length'] = 0

    # Thẻ H1
    h1 = soup.find('h1')
    if h1:
        results['h1'] = h1.text
    else:
        results['h1'] = "Thiếu"

    # Thẻ H2, H3, H4
    for tag in ['h2', 'h3', 'h4']:
        headers = soup.find_all(tag)
        results[f'{tag}_count'] = len(headers)
        results[f'{tag}_text'] = '; '.join(header.text.strip() for header in headers)

    # Kiểm tra văn bản thay thế (Alt text) trong hình ảnh
    images = soup.find_all('img')
    missing_alt = []
    for img in images:
        if not img.get('alt'):
            img_src = urljoin(url, img['src'])
            missing_alt.append(img_src)

    results['image_count'] = len(images)
    results['missing_alt_count'] = len(missing_alt)
    results['missing_alt_links'] = '; '.join(missing_alt)

    # Kiểm tra liên kết nội bộ và ngoại bộ
    internal_links = []
    external_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(url) or href.startswith('/'):
            internal_links.append(urljoin(url, href))
        else:
            external_links.append(href)

    results['internal_links_count'] = len(internal_links)
    results['external_links_count'] = len(external_links)

    # Kiểm tra HTTPS
    results['https'] = url.startswith('https')

    # Kiểm tra robots.txt
    robots_url = urljoin(url, '/robots.txt')
    robots_response = requests.get(robots_url)
    results['robots_txt'] = robots_response.status_code == 200

    # Kiểm tra sitemap.xml
    sitemap_url = urljoin(url, '/sitemap.xml')
    sitemap_response = requests.get(sitemap_url)
    results['sitemap'] = sitemap_response.status_code == 200

    # Kiểm tra thẻ canonical
    canonical = soup.find('link', rel='canonical')
    if canonical:
        results['canonical'] = canonical['href']
    else:
        results['canonical'] = "Không tìm thấy"

    # Kiểm tra tiêu đề trùng lặp
    titles = [title.text for title in soup.find_all('title')]
    results['duplicate_title'] = len(titles) != len(set(titles))

    # Kiểm tra Google Analytics
    ga_code = re.search(r'UA-\d{4,10}-\d{1,4}', page_content)
    if ga_code:
        results['google_analytics'] = ga_code.group(0)
    else:
        results['google_analytics'] = "Không tìm thấy"

    # Kiểm tra favicon
    favicon = soup.find('link', rel='icon')
    if favicon:
        results['favicon'] = favicon['href']
    else:
        results['favicon'] = "Không tìm thấy"

    return results, internal_links

def crawl_website(url, max_pages=50):
    to_crawl = [url]
    crawled = set()
    results = []

    while to_crawl and len(crawled) < max_pages:
        current_url = to_crawl.pop(0)
        if current_url not in crawled:
            print(f"Đang kiểm tra: {current_url}")
            result, internal_links = check_seo(current_url)
            results.append(result)
            crawled.add(current_url)
            for link in internal_links:
                if link not in crawled and link not in to_crawl:
                    to_crawl.append(link)
            time.sleep(1)  # Đợi 1 giây giữa các yêu cầu để tránh bị chặn

    return results

def save_to_txt(filename, results):
    with open(filename, 'w', encoding='utf-8') as output_file:
        for result in results:
            for key, value in result.items():
                output_file.write(f"{key}: {value}\n")
            output_file.write("\n")

if __name__ == "__main__":
    url = input("Nhập URL của trang web: ")
    results = crawl_website(url)
    save_to_txt('seo_results.txt', results)
    print("Đã lưu kết quả kiểm tra SEO vào tệp seo_results.txt")
