import requests
from bs4 import BeautifulSoup
import time
import random

def crawl_data_and_post(url, title_selector, content_selector, api_url, api_data, retries=3):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
    ]
    
    attempt = 0
    while attempt < retries:
        try:
            # Chọn ngẫu nhiên một User-Agent từ danh sách
            headers = {
                'User-Agent': random.choice(user_agents)
            }

            # Gửi yêu cầu HTTP để lấy nội dung của trang web với User-Agent ngẫu nhiên
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Kiểm tra nếu có lỗi xảy ra

            # Phân tích HTML của trang web
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lấy tiêu đề và nội dung theo selector
            title = soup.select_one(title_selector).get_text(strip=True)
            content = soup.select_one(content_selector).prettify()  # Lấy toàn bộ HTML của phần tử

            # Cập nhật dữ liệu API với tiêu đề và nội dung lấy được
            api_data['name'] = title
            api_data['content'] = content

            # Gửi dữ liệu lên API
            post_response = requests.post(api_url, json=api_data)
            post_response.raise_for_status()  # Kiểm tra nếu có lỗi xảy ra khi gửi dữ liệu lên API

            print(f"Data successfully posted to API at {api_url}")
            break

        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                print("Retrying...")
                time.sleep(5)  # Chờ 5 giây trước khi thử lại
            else:
                print("Max retries reached. Exiting.")
        except AttributeError:
            print("Error: Could not find the elements with the provided selectors.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

# Sử dụng hàm này với URL và selector mà bạn muốn
url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6322459/"
title_selector = "h1.content-title"
content_selector = "div.article"
api_url = "https://demo.dongtamcorp.com/api/v1/createPost"
api_data = {
    "name": "admin",       # Đây là chỗ mình sẽ thay thế bằng title lấy được
    "content": "@@Hoquynh1234??",  # Đây là chỗ mình sẽ thay thế bằng content lấy được
    "image": "dsdsadsa"    # Bạn có thể cập nhật giá trị này nếu cần
}

crawl_data_and_post(url, title_selector, content_selector, api_url, api_data)
