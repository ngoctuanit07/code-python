import requests
import os
import sys
import codecs

# Thay đổi mã hóa đầu ra của hệ thống thành UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
def download_image(url, save_path):
    try:
        # Gửi yêu cầu HTTP GET để tải hình ảnh từ URL
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Lấy tên tệp từ URL
        filename = os.path.basename(url)
        full_path = os.path.join(save_path, filename)

        # Lưu hình ảnh vào tệp
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        
        print(f"Tải hình ảnh thành công: {full_path}")
    except requests.exceptions.RequestException as e:
        print(f"Không thể tải hình ảnh: {e}")

# Ví dụ sử dụng
image_url = "https://insangtaotre.vn/wp-content/uploads/2021/08/b5cf811393c6ae436b14456d7a7eefb6.jpg"
save_directory = "./images"  # Đường dẫn thư mục để lưu hình ảnh

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

download_image(image_url, save_directory)
