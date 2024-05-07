import requests

def download_image(image_url, save_path):
    """
    Tải ảnh từ URL và lưu vào đường dẫn chỉ định.

    Args:
    image_url (str): URL của ảnh cần tải.
    save_path (str): Đường dẫn tệp nơi ảnh sẽ được lưu.

    Returns:
    bool: Trả về True nếu tải và lưu thành công, ngược lại False.
    """
    try:
        # Gửi yêu cầu GET đến URL
        response = requests.get(image_url)
        response.raise_for_status()  # Phát sinh lỗi nếu yêu cầu không thành công
        
        # Mở tệp với chế độ write-binary để ghi dữ liệu
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False

# Sử dụng hàm
image_url = "https://cdn.tuoitre.vn/thumb_w/730/471584752817336320/2023/12/28/base64-17037468794361661310140.jpeg"  # Thay thế URL của bạn ở đây
save_path = "base64-17037468794361661310140.jpeg"  # Thay thế đường dẫn lưu ảnh của bạn ở đây
if download_image(image_url, save_path):
    print("Image downloaded successfully.")
else:
    print("Failed to download image.")
