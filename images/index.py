import os
from PIL import Image

def convert_jfif_to_jpg(folder_path):
    # Kiểm tra thư mục có tồn tại hay không
    if not os.path.exists(folder_path):
        print(f"Thư mục {folder_path} không tồn tại.")
        return

    # Lấy danh sách các tệp trong thư mục
    files = os.listdir(folder_path)

    # Lặp qua từng tệp trong thư mục
    for file_name in files:
        if file_name.lower().endswith('.jfif'):
            # Tạo đường dẫn đầy đủ tới tệp
            file_path = os.path.join(folder_path, file_name)
            
            # Mở và chuyển đổi tệp JFIF sang JPG
            with Image.open(file_path) as img:
                # Thay đổi phần mở rộng của tệp
                new_file_name = file_name.rsplit('.', 1)[0] + '.jpg'
                new_file_path = os.path.join(folder_path, new_file_name)
                
                # Lưu tệp mới dưới định dạng JPG
                img.save(new_file_path, 'JPEG')
                
                print(f"Đã chuyển đổi: {file_name} -> {new_file_name}")
    
    print("Hoàn thành chuyển đổi các tệp JFIF sang JPG.")

# Sử dụng hàm
folder_path = 'D:\\tools\\dv\\images\\img'  # Thay đường dẫn này bằng đường dẫn tới thư mục của bạn
convert_jfif_to_jpg(folder_path)
