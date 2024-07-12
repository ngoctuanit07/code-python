import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Đảm bảo mã hóa đúng
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def get_all_links(url, base_url):
    html_content = fetch_page(url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    links = set()

    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        parsed_url = urlparse(full_url)
        if parsed_url.netloc == urlparse(base_url).netloc:
            links.add(full_url)

    return links

def check_broken_links(urls):
    broken_links = []
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                broken_links.append(url)
        except requests.RequestException:
            broken_links.append(url)
    return broken_links

def check_seo_criteria(soup):
    seo_results = {}

    # Thẻ tiêu đề
    title_tag = soup.find('title')
    seo_results['title'] = title_tag.text if title_tag else 'Không có thẻ tiêu đề'

    # Thẻ mô tả
    description_tag = soup.find('meta', attrs={'name': 'description'})
    seo_results['description'] = description_tag['content'] if description_tag else 'Không có thẻ mô tả'

    # Thẻ H1
    h1_tags = soup.find_all('h1')
    seo_results['h1'] = [h1.text.strip() for h1 in h1_tags] if h1_tags else ['Không có thẻ H1']

    # Kiểm tra thẻ alt của hình ảnh
    images = soup.find_all('img')
    seo_results['images_without_alt'] = [img['src'] for img in images if not img.get('alt')]
    seo_results['images_with_alt'] = [img['src'] for img in images if img.get('alt')]

    # Kiểm tra thẻ canonical
    canonical_tag = soup.find('link', rel='canonical')
    seo_results['canonical'] = canonical_tag['href'] if canonical_tag else 'Không có thẻ canonical'

    return seo_results

def audit_seo(url, base_url):
    html_content = fetch_page(url)
    if html_content is None:
        return

    soup = BeautifulSoup(html_content, 'lxml')

    seo_results = check_seo_criteria(soup)

    # Kiểm tra liên kết bị hỏng
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    full_links = [urljoin(url, link) for link in links]
    broken_links = check_broken_links(full_links)

    # Kiểm tra tệp robots.txt
    robots_url = urljoin(base_url, '/robots.txt')
    robots_exists = requests.get(robots_url).status_code == 200

    # Kiểm tra tệp sitemap.xml
    sitemap_url = urljoin(base_url, '/sitemap.xml')
    sitemap_exists = requests.get(sitemap_url).status_code == 200

    # Kiểm tra HTTPS
    parsed_url = urlparse(base_url)
    https = parsed_url.scheme == 'https'

    # Kết quả
    print(f"URL: {url}")
    print(f"Thẻ tiêu đề: {seo_results['title']}")
    print(f"Thẻ mô tả: {seo_results['description']}")
    print(f"Thẻ H1: {seo_results['h1']}")
    print(f"Hình ảnh có thẻ alt: {len(seo_results['images_with_alt'])}")
    print(f"Hình ảnh không có thẻ alt: {len(seo_results['images_without_alt'])}")
    if seo_results['images_without_alt']:
        print("Danh sách hình ảnh không có thẻ alt:")
        for img in seo_results['images_without_alt']:
            print(f" - {img}")
    print(f"Liên kết bị hỏng: {len(broken_links)}")
    if broken_links:
        print("Danh sách liên kết bị hỏng:")
        for link in broken_links:
            print(f" - {link}")
    print(f"Thẻ canonical: {seo_results['canonical']}")
    print(f"Tệp robots.txt tồn tại: {'Có' if robots_exists else 'Không'}")
    print(f"Tệp sitemap.xml tồn tại: {'Có' if sitemap_exists else 'Không'}")
    print(f"Sử dụng HTTPS: {'Có' if https else 'Không'}")
    print("-" * 50)

if __name__ == "__main__":
    base_url = input("Nhập URL của website: ")
    all_links = get_all_links(base_url, base_url)

    print(f"Đã tìm thấy {len(all_links)} liên kết trên trang web.")
    for link in all_links:
        audit_seo(link, base_url)
