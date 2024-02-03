import requests
from bs4 import BeautifulSoup

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
url = "https://chungkhoan.giaodienwebmau.com/" # Thay thế "https://example.com" bằng URL bạn muốn
file_path = "links.txt"
save_links_to_file(url, file_path)
