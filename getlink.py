import requests
from bs4 import BeautifulSoup
import re
from requests.auth import HTTPBasicAuth

# Định nghĩa các thông tin cần thiết cho WordPress
url = 'https://data.nguyenngoctuan07.com'
user_name = 'admin'
password = 'oj6g JyhH Mr6d gN6x yqZy XVyG'

# Hàm lấy token từ WordPress
def get_wp_token(url, user_name, password):
    token_url = f'{url}/wp-json/jwt-auth/v1/token'
    token_data = {'username': user_name, 'password': password}
    try:
        token_response = requests.post(token_url, data=token_data, auth=HTTPBasicAuth(user_name, password))
        token_response.raise_for_status()  # Ném exception nếu có lỗi HTTP
        if token_response.status_code == 200:
            return token_response.json()['token']
        else:
            print(f"Không thể lấy token. Mã trạng thái: {token_response.status_code}")
            print(token_response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối: {e}")
        return None


# Hàm tạo category trên WordPress
def create_wp_category(url, token, name, slug):
    headers = {'Authorization': 'Bearer ' + token}
    category_data = {'name': name, 'slug': slug}
    category_url = f'{url}/wp-json/wp/v2/categories'
    category_response = requests.post(category_url, headers=headers, json=category_data)
    if category_response.status_code == 201:
        return category_response.json()['id']
    else:
        print("Không thể tạo category")
        return None

# Hàm đăng bài viết lên WordPress
def post_to_wp(url, token, title, content, category_id):
    headers = {'Authorization': 'Bearer ' + token}
    post_data = {'title': title, 'content': content, 'status': 'publish', 'categories': [category_id]}
    post_url = f'{url}/wp-json/wp/v2/posts'
    post_response = requests.post(post_url, headers=headers, json=post_data)
    if post_response.status_code == 201:
        print(f"Đã đăng bài viết: {title}")
    else:
        print("Không thể đăng bài viết")

# Hàm làm sạch chuỗi để sử dụng làm tên file
def valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# Hàm lấy dữ liệu từ các link và đăng lên WordPress
def fetch_data_and_post(url, file_path, wp_url, user_name, password):
    token = get_wp_token(wp_url, user_name, password)
    if not token:
        return

    #category_id = 2;#create_wp_category(wp_url, token, 'Auto Category', 'auto-category')
    #if not category_id:
        #return

    with open(file_path, 'r', encoding='utf-8') as file:
        links = file.readlines()

    for link in links:
        link = link.strip()
        if "category" not in link:
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('h1', class_='entry-title').text.strip() if soup.find('h1', class_='entry-title') else 'No Title'
                    content_html = str(soup.find('div', id='content')) if soup.find('div', id='content') else 'No Content'
                    post_to_wp(wp_url, token, title, content_html, 2)
            except Exception as e:
                print(f"Không thể tải dữ liệu từ '{link}': {e}")

# Khởi tạo và sử dụng hàm
def save_links_to_file(url, file_path):
    try:
        # Gửi yêu cầu GET đến URL
        response = requests.get(url)
        # Nếu yêu cầu thành công, tiếp tục
        if response.status_code == 200:
            # Phân tích cú pháp HTML của trang web
            soup = BeautifulSoup(response.text, 'html.parser')
            # Tìm tất cả các thẻ <a> và lấy thuộc tính 'href' (liên kết)
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            # Loại bỏ các liên kết trùng lặp
            links = list(set(links))
            # Mở tệp để ghi
            with open(file_path, 'w', encoding='utf-8') as file:
                for link in links:
                    file.write(f"{link}\n")
            print(f"Đã lưu {len(links)} liên kết vào '{file_path}'")
        else:
            print("Không thể truy cập trang web.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Sử dụng hàm
url1 = "https://tintuc21.giaodienwebmau.com/" # Thay thế "https://example.com" bằng URL bạn muốn

file_path = "links.txt"
wp_url = url  # URL của WordPress
save_links_to_file(url1, file_path)
fetch_data_and_post(url, file_path, wp_url, user_name, password)

