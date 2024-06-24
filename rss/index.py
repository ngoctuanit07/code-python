import feedparser
import requests
from bs4 import BeautifulSoup
import re
import os

def sanitize_title(title):
    # Loại bỏ các ký tự không hợp lệ cho tên file
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_image(image_url, image_path):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(image_path, 'wb') as out_file:
            out_file.write(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")

def crawl_rss_to_txt_files(rss_url, output_dir, css_selectors):
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    
    # Tạo thư mục đầu ra nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate through each entry in the feed
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        description = entry.description
        
        # Sử dụng BeautifulSoup để lấy link ảnh từ thẻ description
        soup = BeautifulSoup(description, 'html.parser')
        image_tag = soup.find('img')
        if image_tag and 'src' in image_tag.attrs:
            image_url = image_tag['src']
        else:
            image_url = None
        
        sanitized_title = sanitize_title(title)
        output_file = os.path.join(output_dir, f"{sanitized_title}.txt")
        image_file = os.path.join(output_dir, f"img_{sanitized_title}.jpg")
        
        # Fetch the full content from the article link
        try:
            response = requests.get(link)
            response.raise_for_status()
            article_content = response.content
            
            # Use BeautifulSoup to parse the article content
            soup = BeautifulSoup(article_content, 'html.parser')
            
            # Extract content based on CSS selectors
            content_parts = []
            for css_selector in css_selectors:
                selected_elements = soup.select(css_selector)
                for element in selected_elements:
                    content_parts.append(element.get_text(strip=True))
            
            # Combine all parts into full text
            full_text = '\n'.join(content_parts)
        except Exception as e:
            full_text = f"Error fetching content: {e}"

        # Write entry details to the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Download and save the image if the URL is found
        if image_url:
            download_image(image_url, image_file)

    print(f'Data has been written to directory {output_dir}')

# Example usage
rss_url = 'https://vnexpress.net/rss/khoa-hoc.rss'
output_dir = 'rss_articles'
css_selectors = ['.title-detail', '.fck_detail']  # Thay thế bằng CSS selectors bạn muốn lấy
crawl_rss_to_txt_files(rss_url, output_dir, css_selectors)
