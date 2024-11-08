import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import base64
import re

def download_images(url):
    # Tạo thư mục 'images' nếu chưa tồn tại
    if not os.path.exists('images'):
        os.makedirs('images')

    # Gửi yêu cầu GET tới URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Không thể truy cập {url}")
        return

    # Phân tích HTML bằng BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả thẻ <img>
    img_tags = soup.find_all('img')

    # Duyệt qua từng thẻ <img> và tải hình ảnh
    for img in img_tags:
        img_url = img.get('src')
        if not img_url:
            continue

        if img_url.startswith('data:image'):  # Kiểm tra nếu ảnh là dạng data URL
            # Kiểm tra xem có phải base64 không
            if ";base64," in img_url:
                # Xử lý base64
                match = re.match(r'data:image/(.*?);base64,(.*)', img_url)
                if match:
                    img_extension = match.group(1)  # Lấy định dạng ảnh
                    img_data = match.group(2)  # Chuỗi base64
                    img_name = f"image_{img_tags.index(img)}.{img_extension}"  # Đặt tên ảnh

                    # Giải mã base64 và lưu file
                    img_bytes = base64.b64decode(img_data)
                    with open(os.path.join('images', img_name), 'wb') as f:
                        f.write(img_bytes)
                    print(f"Tải thành công {img_name}")
                else:
                    print(f"Không thể giải mã chuỗi base64: {img_url}")
            else:
                # Xử lý URL-encoded (dạng không base64)
                img_url_decoded = urllib.parse.unquote(img_url)
                match = re.match(r'data:image/(.*?),(.*)', img_url_decoded)
                if match:
                    img_extension = match.group(1)  # Lấy định dạng ảnh (vd: svg+xml)
                    img_data = match.group(2)  # Dữ liệu ảnh đã giải mã
                    img_name = f"image_{img_tags.index(img)}.{img_extension.split('+')[0]}"  # Đặt tên ảnh

                    # Lưu file ảnh
                    with open(os.path.join('images', img_name), 'w', encoding='utf-8') as f:
                        f.write(img_data)
                    print(f"Tải thành công {img_name}")
                else:
                    print(f"Không thể giải mã chuỗi URL-encoded: {img_url}")
        else:
            # Xử lý URL ảnh bình thường
            img_url = urllib.parse.urljoin(url, img_url)

            # Lấy tên file ảnh
            img_name = os.path.basename(img_url)
            # Nếu tên file không hợp lệ, bỏ qua
            if not img_name:
                continue

            # Tải ảnh từ URL
            try:
                img_data = requests.get(img_url).content
                with open(os.path.join('images', img_name), 'wb') as f:
                    f.write(img_data)
                print(f"Tải thành công {img_name}")
            except Exception as e:
                print(f"Không thể tải {img_url}: {e}")

if __name__ == "__main__":
    url_input = input("Nhập URL trang web: ")
    download_images(url_input)
